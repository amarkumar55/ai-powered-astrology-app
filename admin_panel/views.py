from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta, datetime
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import openai
from django.conf import settings
from django.contrib import messages
import psutil
from authentication.models import UserActivity
from horoscope.models import Horoscope
from panchang.models  import Panchang
from .models import ( SiteSettings,AppLog )
from kundli.models import KundliReport
from invoice.models import Invoice
from subscription.models import UserSubscription, Plan
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from .utlity import handle_file_upload
from django.db.models import Q
from subscription.models import UserTransaction
from django.urls import  reverse
from dasha.models import DashaEffect
from blogs.models import BlogPost, BlogCategory, BlogComment
from .forms import DashaEffectForm, CategoryForm, PlanForm, BlogPostForm, HoroscopeForm, DashaEffectForm, PanchangForm
from django.views.decorators.http import require_GET
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, user_passes_test

User = get_user_model()

def is_admin(user):
    return True

# Create your views here.


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Admin dashboard view displaying system statistics and recent user activities.

    Only accessible by admin users. Shows CPU and memory usage using psutil,
    and fetches the latest 10 user activities.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered admin dashboard page.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
    except Exception as e:
        cpu_usage = memory_usage = None
        messages.warning(request, f"System statistics not available: {str(e)}")

    recent_activities = UserActivity.objects.select_related('user').order_by('-action_date_time')[:10]

    context = {
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'recent_activities': recent_activities,
        'page_title': 'General Statistics'
    }

    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """
    Admin Analytics dashboard view displaying system and revenue statistics.

    Only accessible by admin users. Shows subscriptions, users, kundli repots growth.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered admin dashboard page.
    """
        
    if not is_admin(request.user):
        return redirect('auth.login')

    # Date setup
    end_date = timezone.now()
    start_date = end_date - timedelta(days=180)  # Last 6 months

    # Basic stats
    total_users = User.objects.count()
    new_users_monthly = User.objects.filter(date_joined__gt=start_date).count()
    active_users = User.objects.filter(is_active=True).count()

    total_subscriptions = UserSubscription.objects.count()
    active_subscriptions = UserSubscription.objects.filter(status='active').count()
    trial_subscriptions = UserSubscription.objects.filter(status='active', is_trial=True).count()

    total_kundli_reports = KundliReport.objects.count()
    total_premium = KundliReport.objects.filter(paid=True).count()
    monthlty_premium = KundliReport.objects.filter(paid=True, created_at__gt=start_date).count()

    total_revenue = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(created_at__gt=start_date).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    yearly_revenue = Invoice.objects.filter(created_at__gt=end_date - timedelta(days=365)).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Generate monthly data
    user_growth = (
        User.objects
        .filter(date_joined__gte=start_date)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    kundli_reports = (
        KundliReport.objects
        .filter(created_at__gte=start_date)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    subscriptions = (
        UserSubscription.objects
        .filter(created_at__gte=start_date)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    revenues = (
        Invoice.objects
        .filter(created_at__gte=start_date)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('month')
    )

    # Prepare chart data
    months = []
    monthly_users = []
    monthly_kundlis = []
    monthly_subs = []
    monthly_rev = []

    all_months = sorted(set(
        [entry['month'] for entry in user_growth] +
        [entry['month'] for entry in kundli_reports] +
        [entry['month'] for entry in subscriptions] +
        [entry['month'] for entry in revenues]
    ))

    for month in all_months:
        months.append(month.strftime('%b %Y'))  # e.g. "Jun 2024"

        def get_count(data, m):
            return next((item['count'] for item in data if item['month'] == m), 0)

        def get_sum(data, m):
            return next((item['total'] for item in data if item['month'] == m), 0)

        monthly_users.append(get_count(user_growth, month))
        monthly_kundlis.append(get_count(kundli_reports, month))
        monthly_subs.append(get_count(subscriptions, month))
        monthly_rev.append(get_sum(revenues, month))

    context = {
        'total_users': total_users,
        'new_users_monthly': new_users_monthly,
        'active_users': active_users,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'trial_subscriptions': trial_subscriptions,
        'total_kundli_reports': total_kundli_reports,
        'total_premium': total_premium,
        'monthlty_premium': monthlty_premium,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        'chart_data': {
            'dates': json.dumps(months),
            'total_users': json.dumps(monthly_users),
            'kundli_reports': json.dumps(monthly_kundlis),
            'revenue': json.dumps(monthly_rev),
            'total_subscription': json.dumps(monthly_subs),
        },
        'page_title' : 'Analytics Statistics'
    }

    return render(request, 'admin_panel/analytics/dashboard.html', context)

def blogs_list(request):
    """
    Display a list of blogs.

    Shows all existing blogs list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the bkogs list template with all blogs.

    """
        
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    posts = BlogPost.objects.select_related('category', 'author').all()
    
    # Apply filters
    if status:
        posts = posts.filter(status=status)
    if category:
        posts = posts.filter(category_id=category)
    if search:
        posts = posts.filter(title__icontains=search)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    
    # Get categories for filter
    categories = BlogCategory.objects.all()

    status_choices = {
        'draft': 'Draft',
        'published': 'Published',
        'archived': 'Archived',
    }
    
    context = {
        'posts': posts,
        'categories': categories,
        'status': status,
        'category_filter': category,
        'search': search,
        'page_title' : 'Posts List',
        'status_choices':status_choices,
    }
    return render(request, 'admin_panel/blogs/list.html', context)

def blog_detail(request, blog_id):
    """
    View detailed information of a blog post including its comments.

    Only accessible by admin users. Retrieves the blog post by its ID,
    along with associated comments, and renders them in the detail template.

    Args:
        request (HttpRequest): The incoming HTTP request.
        blog_id (int): The ID of the blog post to display.

    Returns:
        HttpResponse: Renders the blog detail template with post and comment data.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    post = get_object_or_404(
        BlogPost.objects.select_related('category', 'author'),
        id=blog_id
    )
    
    comments = BlogComment.objects.filter(post=post)\
                .select_related('author', 'parent')\
                .order_by('-created_at')  # Optional: sort comments

    context = {
        'post': post,
        'comments': comments,
        'page_title': 'Post Information'
    }

    return render(request, 'admin_panel/blogs/detail.html', context)

def blog_create(request):
    """
    View to create a new blog post.

    Only accessible by admin users. Handles both GET (to render form)
    and POST (to process submitted form and create blog post).

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders blog creation form or redirects to detail view on success.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user

                # Generate unique slug
                base_slug = slugify(post.title)
                slug = base_slug
                counter = 1
                while BlogPost.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                post.slug = slug

                # Handle image upload
                if 'featured_image' in request.FILES:
                    post.featured_image = handle_file_upload(request.FILES['featured_image'])

                post.save()
                messages.success(request, 'Blog post created successfully.')
                return redirect('admin_panel:admin_blog_detail', blog_id=post.id)

            except IntegrityError:
                messages.error(request, 'A blog post with similar details already exists.')
            except Exception as e:
                messages.error(request, f"Unexpected error: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm()

    context = {
        'form': form,
        'categories': BlogCategory.objects.all(),
        'CSP_NONCE': getattr(request, "csp_nonce", ""),
        'page_title': 'Create a New Post'
    }
    return render(request, 'admin_panel/blogs/create.html', context)
def blog_edit(request, blog_id):
    """
    View to edit an existing blog post.

    Only accessible by admin users. On GET, renders the blog edit form pre-filled
    with post data. On POST, validates and updates the blog post and ensures 
    a unique slug is maintained.

    Args:
        request (HttpRequest): The HTTP request object.
        blog_id (int): ID of the blog post to edit.

    Returns:
        HttpResponse: Rendered template or redirect after successful update.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    post = get_object_or_404(BlogPost, id=blog_id)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)

            # Recalculate unique slug if title or slug is changed
            base_slug = slugify(post.title)
            slug = base_slug
            counter = 1
            while BlogPost.objects.exclude(id=post.id).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            post.slug = slug

            # Handle featured image if new one is uploaded
            if 'featured_image' in request.FILES:
                post.featured_image = handle_file_upload(request.FILES['featured_image'])

            post.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('admin_panel:admin_blog_detail', blog_id=post.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogPostForm(instance=post)

    context = {
        'form': form,
        'categories': BlogCategory.objects.all(),
        'post': post,
        'page_title': 'Edit Post Information',
        'CSP_NONCE': getattr(request, "csp_nonce", ""),
    }
    return render(request, 'admin_panel/blogs/edit.html', context)


def blog_delete(request, blog_id):
    """
    View to delete a blog post by ID.

    Only accessible by admin users. Deletes the post if it exists,
    otherwise shows an error message.

    Args:
        request (HttpRequest): The HTTP request.
        blog_id (int): ID of the blog post to delete.

    Returns:
        HttpResponseRedirect: Redirects to the blog list view.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    post = get_object_or_404(BlogPost, id=blog_id)
    post.delete()
    messages.success(request, 'Blog post deleted successfully.')
    return redirect('admin_panel:admin_blogs')

def blog_comment_approve(request, comment_id):
    """
    Approves a blog comment by its ID.

    Only accessible by admin users. If the comment is found, sets it as approved
    and redirects to the blog detail page. If not found, shows an error and redirects
    to the blogs list.

    Args:
        request (HttpRequest): The incoming HTTP request.
        comment_id (int): The ID of the comment to approve.

    Returns:
        HttpResponseRedirect: Redirect to blog detail or blog list.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    try:
        comment = BlogComment.objects.select_related('post').get(id=comment_id)
        comment.is_approved = True
        comment.save()
        messages.success(request, 'Comment approved successfully.')
        return redirect('admin_panel:admin_blog_detail', blog_id=comment.post.id)

    except BlogComment.DoesNotExist:
        messages.error(request, 'Comment not found.')
        return redirect('admin_panel:admin_blogs')

def blog_comment_delete(request, comment_id):
    """
    Deletes a blog comment by its ID.

    Only accessible by admin users. If the comment is found, deletes it and 
    redirects to the related blog post detail page. If not found, redirects to 
    the blog list with an error message.

    Args:
        request (HttpRequest): The incoming HTTP request.
        comment_id (int): The ID of the comment to delete.

    Returns:
        HttpResponseRedirect: Redirect to blog detail or blog list.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    try:
        comment = BlogComment.objects.select_related('post').get(id=comment_id)
        post_id = comment.post.id
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('admin_panel:admin_blog_detail', blog_id=post_id)

    except BlogComment.DoesNotExist:
        messages.error(request, 'Comment not found.')
        return redirect('admin_panel:admin_blogs')

#### start of users handling ####

def users_list(request):
    """
    Display a list of users.

    Shows all existing users list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the users list template with all users.

    """
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    role = request.GET.get('role','user')
    
    # Base queryset
    users = User.objects.all()
    
    # Apply filters
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search) | users.filter(first_name__icontains=search) | users.filter(last_name__icontains=search)
  
    if status:
        users = users.filter(is_active=(status == 'active'))

    if role: 
        if role == 'admin':
           users = users.filter(is_admin=True)
        elif role == 'staff':
           users = users.filter(is_staff=True)
        else:
            users = users.filter(is_user=True)

               
    # Pagination
    paginator = Paginator(users, 10)
    page = request.GET.get('page', 1)
    users = paginator.get_page(page)
    role_choices = {
        'admin' : 'Admin',
        'staff' : 'Staff',
        'user' : 'User'
    }

    status_choices = {
        'active' : 'Active',
        'inactive' : 'Inactive',
    }
   
    context = {
        'users': users,
        'search': search,
        'status': status,
        'page_title' : 'Users List',
        'role_choices': role_choices,
        'status_choices':status_choices,
    }

    return render(request, 'admin_panel/users/list.html', context)

@require_GET
def user_detail(request, user_id):
    """
    View to display detailed user information, including subscriptions and activity logs.

    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP GET request.
        user_id (int): The ID of the user whose details are to be shown.

    Returns:
        HttpResponse: Renders the user detail template with user data, subscriptions, and recent activities.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    user = get_object_or_404(User, id=user_id)
    subscriptions = UserSubscription.objects.filter(user=user)
    activities = UserActivity.objects.filter(user=user).order_by('-action_date_time')[:10]

    context = {
        'user': user,
        'subscriptions': subscriptions,
        'activities': activities,
        'page_title': 'User Information'
    }
    return render(request, 'admin_panel/users/detail.html', context)

def user_edit(request, user_id):
    """
    View to edit basic user attributes (is_active, is_staff, is_admin).

    Only accessible by admin users. Handles GET to render user edit form,
    and POST to update user flags.

    Args:
        request (HttpRequest): The incoming HTTP request.
        user_id (int): The ID of the user to edit.

    Returns:
        HttpResponse: Renders the user edit template or redirects after update.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    user = get_object_or_404(User, id=user_id)

    # Prevent editing self or superuser (optional but safer)
    if user == request.user:
        messages.warning(request, "You cannot edit your own permissions.")
        return redirect('admin_panel:admin_user_detail', user_id=user.id)
    
    if request.method == 'POST':
        try:
            is_active = request.POST.get('is_active') == 'on'
            is_staff = request.POST.get('is_staff') == 'on'

            # Optional: prevent non-superadmins from modifying staff/admin flags
            if not request.user.is_superuser:
                messages.error(request, "Only superusers can modify user roles.")
                return redirect('admin_panel:admin_user_detail', user_id=user.id)

            user.is_active = is_active
            user.is_staff = is_staff
            user.is_admin = is_staff  # Assuming is_admin is a custom field based on is_staff

            user.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_panel:admin_user_detail', user_id=user.id)

        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')

    context = {
        'user': user,
        'page_title': 'Edit User Information'
    }
    return render(request, 'admin_panel/users/edit.html', context)

#### end of users handling ####


#### start of subscriptions handling ####
def subscriptions(request):
    """
    Display a list of subscriptions.

    Shows all existing subscriptions list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the subscriptions list template with all subscriptions.

    """
      
    if not is_admin(request.user):
        return redirect('auth.login')

    # Get filter parameters from POST or GET for flexibility
    email = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip().lower()
    start_date_str = request.GET.get('start_date', '').strip()
    end_date_str = request.GET.get('end_date', '').strip()

    # Base queryset
    subscriptions = UserSubscription.objects.select_related('user', 'plan').all().order_by('-created_at')

    # Apply filters
    if email:
        subscriptions = subscriptions.filter(user__email__icontains=email)

    if status in ['active', 'expired', 'cancelled']:
        subscriptions = subscriptions.filter(status=status)

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            subscriptions = subscriptions.filter(start_date__date__gte=start_date.date())
        except ValueError:
            pass  # invalid date ignored

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            subscriptions = subscriptions.filter(end_date__date__lte=end_date.date())
        except ValueError:
            pass  # invalid date ignored

    # Pagination
    paginator = Paginator(subscriptions, 50)
    page = request.GET.get('page', 1)
    subscriptions_page = paginator.get_page(page)

    status_choices = {
        'active': 'Active',
        'expired': 'Expired',
        'cancelled': 'Cancelled',
    }

    context = {
        'subscriptions': subscriptions_page,
        'search': email,
        'status': status,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'page_title' : 'Subscriptions List',
        'status_choices':status_choices,
    }

    return render(request, 'admin_panel/subscriptions/index.html', context)

def subscription_detail(request, subscription_id):
  
    """
    View and update a user's subscription status.

    Only accessible by admin users. Retrieves the subscription by its ID,
    and allows status updates via POST request.

    Args:
        request (HttpRequest): The incoming HTTP request.
        subscription_id (int): The ID of the subscription to edit.

    Returns:
        HttpResponse: Renders the subscription details template or redirects 
                      to the subscription list on successful update.
    """

    if not is_admin(request.user):
        return redirect('auth.login')

    subscription = get_object_or_404(UserSubscription, id=subscription_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed_statuses = ["active", "expired", "cancelled"]
        
        if new_status in allowed_statuses:
            subscription.status = new_status
            subscription.save()
            messages.success(request, "Subscription updated successfully.")
            return redirect('admin_panel:admin_subscription')
        else:
            messages.error(request, "Invalid status selected.")

    context = {
        'subscription': subscription,
        'page_title': 'Subscription Detail'
    }

    return render(request, 'admin_panel/subscriptions/edit.html', context)

#### end of subscriptions handling ####

#### start of plans handling ####

def plans(request):
    """
    Display a list of plans list.

    Shows all existing panchang list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the plans list template with all plans.

    """
        
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')    
    
    # Base queryset
    plans = Plan.objects.all()
    
    # Apply filters
    if search:
        plans = plans.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
   
    if status:
        plans = plans.filter(is_active=(status == '1'))

    # Pagination
    paginator = Paginator(plans, 10)
    page = request.GET.get('page', 1)
    plans = paginator.get_page(page)
    
    status_choices = {
        '1': 'Active',
        '0': 'Disable',
    }
    context = {
        'plans': plans,
        'search': search,
        'status': status,
        'page_title' : 'Plans List',
        'status_choices':status_choices,
    }

    return render(request, 'admin_panel/plans/index.html', context)

def plan_create(request):
    """
    Handle the creation of a new plan.

    Displays a form for creating a new plan and processes form submission.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The HTTP request object, either GET to display the form
            or POST to submit a new plan.

    Returns:
        HttpResponse: Renders the plan creation template or redirects on success.

    """

    if not is_admin(request.user):
        return redirect('auth.login')

    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            try:
                plan = form.save(commit=False)
                # Ensure unique slug
                base_slug = slugify(plan.name)
                slug = base_slug
                counter = 1
                while Plan.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                plan.slug = slug
                plan.save()  # ✅ Save the plan here
                messages.success(request, 'Plan created successfully.')
                return redirect('admin_panel:admin_plans')
            except Exception as e:
                messages.error(request, f'Error creating plan: {str(e)}')
        else: 
            messages.error(request, "Please correct the errors below.")
    else:
        form = PlanForm()

    return render(request, 'admin_panel/plans/create.html', {
        'form': form,  
        'page_title': 'Create a new plan'
    })

def plan_edit(request, plan_id):
    """
    Edit an existing plan details.

    Only accessible by admin users. Retrieves the plan by its ID, 
    displays the form pre-filled with current data, and processes updates 
    after form submission.

    Args:
        request (HttpRequest): The incoming HTTP request.
        plan_id (int): the plan_id to find plan to edit.

    Returns:
        HttpResponse: Renders the edit plan details template or redirects 
                      to the plans list on successful update.
    """

    if not is_admin(request.user):
        return redirect('auth.login')

    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        messages.error(request, 'The requested plan does not exist.')
        return redirect('admin_panel:admin_plans')


    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            try:
                updated_plan = form.save(commit=False)

                # Preserve the existing slug or regenerate if name changed
                base_slug = slugify(updated_plan.name)
                slug = base_slug
                counter = 1
                while Plan.objects.exclude(id=plan.id).filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                updated_plan.slug = slug

                updated_plan.save()
                messages.success(request, 'Subscription plan updated successfully.')
                return redirect('admin_panel:admin_plans')
            except Exception as e:
                messages.error(request, f'Error updating subscription plan: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlanForm(instance=plan)

    context = {
        'form': form,
        'plan': plan,
        'page_title': 'Edit Plan Information'
    }
    return render(request, 'admin_panel/plans/edit.html', context)

def plan_delete(request, plan_id):

    """
        Delete an existing plan.

        Checks for admin access and deletes the specified plan upon POST request.
        Displays success or error messages based on the outcome.

        Args:
            request (HttpRequest): The incoming HTTP request.
            plan_id (int): ID of the plan to delete.

        Returns:
            HttpResponse: Renders the delete confirmation page or redirects after deletion.

    """
   
    if not is_admin(request.user):
        return redirect('auth.login')
    
    try:
        plan = Plan.objects.get(id=plan_id)
        
        # Check if plan has active subscriptions
        active_subscriptions = UserSubscription.objects.filter(
            plan=plan,
            status='active'
        ).exists()
        
        if active_subscriptions:
            messages.error(request, 'Cannot delete plan with active subscriptions.')
            return redirect('admin_panel:admin_subscription_plans')
        
        plan.delete()
        messages.success(request, 'Subscription plan deleted successfully.')
        
    except Plan.DoesNotExist:
        messages.error(request, 'Subscription plan not found.')
    
    return redirect('admin_panel:admin_subscription_plans')

#### end of plans handling ####

#### start of horoscope handling ####

def horoscope_daily_list(request):
    """
    Display a list of daily horoscope list.

    Shows all existing daily horoscope list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the daily horoscope list template with all daily horoscope.

    """
       
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    sign = request.GET.get('sign', '')
    date = request.GET.get('date', '')
    
    # Base queryset
    horoscopes = Horoscope.objects.filter(type='daily').all()
    
    # Apply filters
    if sign:
        horoscopes = horoscopes.filter(sign=sign)
    if date:
        horoscopes = horoscopes.filter(date=date)
    
    # Pagination
    paginator = Paginator(horoscopes, 10)
    page = request.GET.get('page', 1)
    horoscopes = paginator.get_page(page)
    url = reverse('admin_panel:admin_horoscope_daily')

    status_choices = {
       "Taurus" : "Taurus",
       "Gemini" : "Gemini",
       "Cancer" : "Cancer",
       "Leo" : "Leo",
       "Virgo" : "Virgo",
       "Libra" : "Libra",
       "Scorpio": "Scorpio",
       "Sagittarius":"Sagittarius",
       "Capricorn":"Capricorn",
       "Aquarius":"Aquarius",
       "Pisces":"Pisces"
    }
     
    context = {
        'horoscopes': horoscopes,
        'sign': sign,
        'date': date,
        'page_title' : 'Daily Horoscope List',
        'action_url' : url, 
        'status_choices':status_choices,
    }
    return render(request, 'admin_panel/horoscope/index.html', context)

def horoscope_weekly_list(request):
    """
    Display a list of weekly horoscope list.

    Shows all existing weekly horoscope list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the weekly horoscope list template with all weekly horoscope.

    """
      
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    sign = request.GET.get('sign', '')
    date = request.GET.get('date', '')
    
    # Base queryset
    horoscopes = Horoscope.objects.filter(type='weekly').all()
    
    # Apply filters
    if sign:
        horoscopes = horoscopes.filter(sign=sign)
    if date:
        horoscopes = horoscopes.filter(date=date)
    
    # Pagination
    paginator = Paginator(horoscopes, 10)
    page = request.GET.get('page', 1)
    horoscopes = paginator.get_page(page)
    url = reverse('admin_panel:admin_horoscope_weekly')
  
    status_choices = {
       "Taurus" : "Taurus",
       "Gemini" : "Gemini",
       "Cancer" : "Cancer",
       "Leo" : "Leo",
       "Virgo" : "Virgo",
       "Libra" : "Libra",
       "Scorpio": "Scorpio",
       "Sagittarius":"Sagittarius",
       "Capricorn":"Capricorn",
       "Aquarius":"Aquarius",
       "Pisces":"Pisces"
    }
  
    context = {
        'horoscopes': horoscopes,
        'sign': sign,
        'date': date,
        'page_title' : 'Weekly Horoscope List',
        'action_url' : url, 
        'status_choices':status_choices,
    }
    return render(request, 'admin_panel/horoscope/index.html', context)

def horoscope_monthly_list(request):
    """
    Display a list of monthly horoscope list.

    Shows all existing monthly horoscope list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the monthly horoscope list template with all monthly horoscope.

    """
     
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    sign = request.GET.get('sign', '')
    date = request.GET.get('date', '')
    
    # Base queryset
    horoscopes = Horoscope.objects.filter(type='monthly').all()
    
    # Apply filters
    if sign:
        horoscopes = horoscopes.filter(sign=sign)
    if date:
        horoscopes = horoscopes.filter(date=date)
    
    # Pagination
    paginator = Paginator(horoscopes, 10)
    page = request.GET.get('page', 1)
    horoscopes = paginator.get_page(page)
    
    url = reverse('admin_panel:admin_horoscope_monthly')

    status_choices = {
       "Taurus" : "Taurus",
       "Gemini" : "Gemini",
       "Cancer" : "Cancer",
       "Leo" : "Leo",
       "Virgo" : "Virgo",
       "Libra" : "Libra",
       "Scorpio": "Scorpio",
       "Sagittarius":"Sagittarius",
       "Capricorn":"Capricorn",
       "Aquarius":"Aquarius",
       "Pisces":"Pisces"
    }
    
    context = {
        'horoscopes': horoscopes,
        'sign': sign,
        'date': date,
        'action_url' : url, 
        'page_title' : 'Monthly Horoscope List',
        'status_choices':status_choices,
    }
    return render(request, 'admin_panel/horoscope/index.html', context)

def horoscope_yearly_list(request):
    """
    Display a list of yearly horoscope list.

    Shows all existing yearly horoscope list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the yearly horoscope list template with all yearly horoscope.

    """
  
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    sign = request.GET.get('sign', '')
    date = request.GET.get('date', '')
    
    # Base queryset
    horoscopes = Horoscope.objects.filter(type='yearly').all()
    
    # Apply filters
    if sign:
        horoscopes = horoscopes.filter(sign=sign)
    if date:
        horoscopes = horoscopes.filter(date=date)
    
    # Pagination
    paginator = Paginator(horoscopes, 10)
    page = request.GET.get('page', 1)
    horoscopes = paginator.get_page(page)
    url = reverse('admin_panel:admin_horoscope_yearly')
    
    status_choices = {
       "Taurus" : "Taurus",
       "Gemini" : "Gemini",
       "Cancer" : "Cancer",
       "Leo" : "Leo",
       "Virgo" : "Virgo",
       "Libra" : "Libra",
       "Scorpio": "Scorpio",
       "Sagittarius":"Sagittarius",
       "Capricorn":"Capricorn",
       "Aquarius":"Aquarius",
       "Pisces":"Pisces"
    }

    context = {
        'horoscopes': horoscopes,
        'sign': sign,
        'date': date,
        'action_url' : url, 
        'page_title' : 'Yearly Horoscope List',
        'status_choices':status_choices,
    }
    return render(request, 'admin_panel/horoscope/index.html', context)

def horoscope_edit(request, horoscope_id):
    """
    Edit an existing horoscope entry.

    Only accessible by admin users. If the horoscope doesn't exist, user is redirected with an error.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    try:
        horoscope = Horoscope.objects.get(id=horoscope_id)
    except Horoscope.DoesNotExist:
        messages.error(request, 'Horoscope not found.')
        return redirect('admin_panel:admin_horoscope_daily')

    form = HoroscopeForm(request.POST or None, instance=horoscope)

    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Horoscope updated successfully.')
                return redirect('admin_panel:admin_horoscope_daily')
            except Exception as e:
                messages.error(request, f'Error updating horoscope: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'admin_panel/horoscope/details.html', {
        'form': form,
        'horoscope': horoscope,
        'page_title': 'Edit Horoscope Information'
    })

#### end of horoscope handling ####

#### start of panchang handling ####

def panchang_list(request):
    """
    Display a list of panchang list.

    Shows all existing panchang list, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the panchang list template with all panchang.

    """
      
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    date = request.GET.get('date', '')
    
    # Base queryset
    panchangs = Panchang.objects.all().order_by('-date')
    
    # Apply filters
    if date:
        panchangs = panchangs.filter(date=date)
    
    # Pagination
    paginator = Paginator(panchangs, 10)
    page = request.GET.get('page', 1)
    panchangs = paginator.get_page(page)
    
    context = {
        'panchangs': panchangs,
        'date': date,
        'page_title' : 'Panchangs List'
    }

    return render(request, 'admin_panel/panchang/index.html', context)
    
def panchang_edit(request, panchang_id):
    """
    Edit an existing panchang report details.

    Only accessible by admin users. Retrieves the panchang report by its ID, 
    displays the form pre-filled with current data, and processes updates 
    after form submission.

    Args:
        request (HttpRequest): The incoming HTTP request.
        
    Returns:
        HttpResponse: Renders the edit panchang template or redirects 
                      to the panchang list on successful update.
    """

    if not is_admin(request.user):
        return redirect('auth.login')
    
    try:
        panchang = Panchang.objects.get(id=panchang_id)
    except Panchang.DoesNotExist:
        messages.error(request, 'Panchang not found.')
        return redirect('admin_panel:admin_panchang')

    if request.method == 'POST':
        form = PanchangForm(request.POST, instance=panchang)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Panchang updated successfully.')
                return redirect('admin_panel:admin_panchang')
            except Exception as e:
                messages.error(request, f'Error saving panchang: {str(e)}')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PanchangForm(instance=panchang)

    return render(request, 'admin_panel/panchang/edit.html', {
        'form': form,
        'panchang': panchang,
        'page_title': 'Edit Panchang'
    })

#### End of panchang handling ####

#### start of kundli handling ####

def kundli_reports(request):
    """
    Display a list of kundli reports.

    Shows all existing kundli reports, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the kundli list template with all kundli reports.

    """
       
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search = request.GET.get('search', '').strip()
    status  = request.GET.get('status', '').strip()

    kundli_reports = KundliReport.objects.all()

    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    if search:
        kundli_reports = kundli_reports.filter(user__email__icontains=search)

    
    if status: 
        if status == 'paid':
            kundli_reports = kundli_reports.filter(paid=True)
        elif status == 'unpaid':
            kundli_reports = kundli_reports.filter(paid=False)


    kundli_reports = kundli_reports.order_by('-created_at')

    # Pagination
    paginator = Paginator(kundli_reports, 10)
    page = request.GET.get('page')
    kundli_reports = paginator.get_page(page)

    status_choices = {
        'unpaid': 'Unpaid',
        'paid': 'Paid',
    }

    context = {
        'kundli_reports': kundli_reports,
        'start_date': start_date,
        'end_date': end_date,
        'search': search,
        'page_title' : 'Kundli \'s List',
        'status_choices':status_choices,
    }

    return render(request, 'admin_panel/kundli/list.html', context)

def kundli_report_edit(request, report_id=None):
    """
    Edit an existing kundli report details.

    Only accessible by admin users. Retrieves the kundli report by its ID, 
    displays the form pre-filled with current data, and processes updates 
    after form submission.

    Args:
        request (HttpRequest): The incoming HTTP request.
        status (string): The status of the kundli report to edit.

    Returns:
        HttpResponse: Renders the edit kundli report template or redirects 
                      to the kundli report list on successful update.
    """
     
    if not is_admin(request.user):
        return redirect('auth.login')

    try:
        report = get_object_or_404(KundliReport, id=report_id)

        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status in ['paid', 'unpaid']:
               
                if new_status == 'paid':
                   report.status = 1 
                else: 
                   report.staus = 0
                   
                report.save()
               
                messages.success(request, f'Kundlu status updated to {new_status}.')
                return redirect('admin_panel:kundli_report_edit', id=report.id)
            else:
                messages.error(request, 'Invalid status.')
        
        context = {
            'report': report,
            'page_title': 'Edit or View Kundli',
        }

        return render(request, 'admin_panel/kundli/detail.html', context)
        
    except KundliReport.DoesNotExist:
        messages.error(request, 'Kundli Report not found.')
        return redirect('admin_panel:admin_kundli')
#### end of kundli handling ####

#### start of invoices handling ####
def invoices_list(request):
    """
    Display a list of invoices.

    Shows all existing invoices, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the invoices list template with all invoices.

    """
    
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Base queryset
    invoices = Invoice.objects.all()
    
    # Apply filters
    if search:
        invoices = invoices.filter(
            invoice_number__icontains=search
        ) | invoices.filter(
            user__username__icontains=search
        ) | invoices.filter(
            user__email__icontains=search
        )
    if status:
        invoices = invoices.filter(status=status)
    if start_date:
        invoices = invoices.filter(created_at__gte=start_date)
    if end_date:
        invoices = invoices.filter(created_at__lte=end_date)
    
    # Pagination
    paginator = Paginator(invoices, 10)
    page = request.GET.get('page', 1)
    invoices = paginator.get_page(page)

    status_choices = {
        'paid': 'Paid',
        'pending': 'Pending',
        'failed': 'Failed',
    }

    context = {
        'invoices': invoices,
        'search': search,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'page_title' : 'Invoices List',
        'status_choices':status_choices,
    }
    return render(request, 'admin_panel/invoices/index.html', context)

def invoice_detail(request, invoice_id):

    """
    Edit an existing invoice details.

    Only accessible by admin users. Retrieves the invoice by its ID, 
    displays the form pre-filled with current data, and processes updates 
    after form submission.

    Args:
        request (HttpRequest): The incoming HTTP request.
        status (string): The status of the invoice to edit.

    Returns:
        HttpResponse: Renders the edit invoice template or redirects 
                      to the invoice list on successful update.
    """
   
    if not is_admin(request.user):
        return redirect('auth.login')
    
    try:
        invoice = Invoice.objects.get(id=invoice_id)

        # Get related data
        subscription = invoice.subscription
        user = invoice.user

        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status in ['pending', 'paid', 'cancelled', 'refunded']:
                invoice.status = int(new_status)
                invoice.save()
                messages.success(request, f'Invoice status updated to {new_status}.')
                return redirect('admin_panel:admin_invoice_detail', invoice_id=invoice.id)
            else:
                messages.error(request, 'Invalid status.')
        
        context = {
            'invoice': invoice,
            'subscription': subscription,
            'user': user,
            'page_title' : 'Invoice Information'
        }

        return render(request, 'admin_panel/invoices/detail.html', context)
        
    except Invoice.DoesNotExist:
        messages.error(request, 'Invoice not found.')
        return redirect('admin_panel:admin_invoices')
#### End of invoices handling ####

#### start of transactions handling ####
def transactions_list(request):

    """
    Display a list of transactions.

    Shows all existing transactions, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the transactions list template with all transactions effect.

    """
  
    if not is_admin(request.user):
        return redirect('auth.login')
    
    # Get filter parameters
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Base queryset
    transactions = UserTransaction.objects.filter(refund_id__isnull=True).all()
    
    # Apply filters
    if search:
        transactions = transactions.filter(
            user__email__icontains=search
        ) | transactions.filter(
            invoice__invoice_number__icontains=search
        ) 

    if status:
        transactions = transactions.filter(status=status)
    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__lte=end_date)
    
    # Pagination
    paginator = Paginator(transactions, 10)
    page = request.GET.get('page', 1)
    transactions = paginator.get_page(page)

    status_choices = {
        'Pending': 'Pending',
        'Success': 'Success',
        'Failed': 'Failed',
        'Refunded': 'Refunded',
        'Cancelled':'Cancelled',
    }

    context = {
        'transactions': transactions,
        'search': search,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
        'page_title' : 'Transactions List',
        'status_choices':status_choices,
    }

    return render(request, 'admin_panel/payments/transactions.html', context)

#### end of transactions handling ####

#### start of dasha effect handling ####

def dasha_effect(request):
    """
    Display a list of dasha effects.

    Shows all existing dasha effects, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the dasha list template with all dasha effect.

    """
        
    if not is_admin(request.user):
        return redirect('auth.login')

    search = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    dashas = DashaEffect.objects.all().order_by('-start_date')

    # Text-based search
    if search:
        dashas = dashas.filter(
            Q(mahadasha_planet__icontains=search) |
            Q(antar_dasha_planet__icontains=search)
        )

    # Date filters
    if start_date:
        try:
            dashas = dashas.filter(start_date__gte=datetime.strptime(start_date, '%Y-%m-%d'))
        except ValueError:
            pass

    if end_date:
        try:
            dashas = dashas.filter(end_date__lte=datetime.strptime(end_date, '%Y-%m-%d'))
        except ValueError:
            pass

    paginator = Paginator(dashas, 20)
    page = request.GET.get('page')
    dashas = paginator.get_page(page)

    return render(request, 'admin_panel/dasha/list.html', {
        'dashas': dashas,
        'search': search,
        'start_date': start_date,
        'end_date': end_date,
        'page_title' : 'Dasha Effect List'
    })

# ➕ CREATE view
def dasha_effect_create(request):
    """
    Handle the creation of a new dasha effect.

    Displays a form for creating a new dasha effect and processes form submission.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The HTTP request object, either GET to display the form
            or POST to submit a new dasha effect.

    Returns:
        HttpResponse: Renders the dasha effect creation template or redirects on success.

    """
    
    if not is_admin(request.user):
        return redirect('auth.login')

    if request.method == "POST":
        form = DashaEffectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:admin_dasha_effect')
    else:
        form = DashaEffectForm()

    return render(request, 'admin_panel/dasha/create.html', {
        'form': form,
        'page_title': 'Dasha Effect Create'
    })


def dasha_effect_edit(request, dasha_id):
    """
    Edit an existing dasha effect.

    Only accessible by admin users. Retrieves the dasha effect by its ID, 
    displays the form pre-filled with current data, and processes updates 
    after form submission. Validates uniqueness of name and slug.

    Args:
        request (HttpRequest): The incoming HTTP request.
        dasha_id (int): The ID of the dasha effect to edit.

    Returns:
        HttpResponse: Renders the edit dasha effect template or redirects 
                      to the dasha effect list on successful update.
    """
   
    if not is_admin(request.user):
        return redirect('auth.login')

    dasha = get_object_or_404(DashaEffect, id=dasha_id)

    if request.method == "POST":
        form = DashaEffectForm(request.POST, instance=dasha)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Dasha Effect updated successfully.")
                return redirect('admin_panel:admin_dasha_effect')
            except Exception as e:
                messages.error(request, f"Error updating Dasha Effect: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DashaEffectForm(instance=dasha)

    return render(request, 'admin_panel/dasha/details.html', {
        'form': form,
        'dasha': dasha,
        'page_title': 'Edit Dasha Effect Details'
    })


def dasha_effect_delete(request, pk):

    """
        Delete an existing dasha effect.

        Checks for admin access and deletes the specified dasha effect upon POST request.
        Displays success or error messages based on the outcome.

        Args:
            request (HttpRequest): The incoming HTTP request.
            pk (int): ID of the dasha effect to delete.

        Returns:
            HttpResponse: Renders the delete confirmation page or redirects after deletion.

    """
   
    if not is_admin(request.user):
        return redirect('auth.login')
    
    if request.method == 'POST':
        try:
            dasha = get_object_or_404(DashaEffect, pk=pk)
            dasha.delete()
            messages.success(request, 'Dasha deleted successfully!')

        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")
             
    return redirect('admin_panel:admin_dasha_effect')

    
#### End of handling dasha effect ####
    
#### handling of category section #####

def categories_list(request):

    """
    Display a list of blog categories.

    Shows all existing blog categories, possibly with pagination or filtering in the future.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the category list template with all blog categories.

    """


    if not is_admin(request.user):
        return redirect('auth.login')
   
    search = request.GET.get('search', '')

    categories = BlogCategory.objects.all()
   
    if search:
        categories = categories.filter(name__icontains=search)

    paginator = Paginator(categories, 20)
    page = request.GET.get('page')
    categories = paginator.get_page(page)
   
    context = { 
        'categories': categories, 
        'search': search,
        'page_title' : 'Categories List'
    }
    
    return render(request, 'admin_panel/categories/list.html', context)


def category_create(request):
    
    """
    Handle the creation of a new blog category.

    Displays a form for creating a new category and processes form submission.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The HTTP request object, either GET to display the form
            or POST to submit a new category.

    Returns:
        HttpResponse: Renders the category creation template or redirects on success.

    """

    if not is_admin(request.user):
        return redirect('auth.login')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.slug = slugify(category.name)

                # Ensure uniqueness of slug
                if BlogCategory.objects.filter(slug=category.slug).exists():
                    form.add_error('name', 'A category with this slug already exists.')
                else:
                    category.save()
                    messages.success(request, 'Category created successfully!')
                    return redirect('admin_panel:admin_categories')
            except Exception as e:
                messages.error(request, f"Error creating category: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CategoryForm()

    return render(request, 'admin_panel/categories/create.html', {
        'form': form,
        'page_title': 'Create a new category'
    })




def category_edit(request, category_id):
    """
    Edit an existing blog category.

    Only accessible by admin users. Retrieves the category by its ID, 
    displays the form pre-filled with current data, and processes updates 
    after form submission. Validates uniqueness of name and slug.

    Args:
        request (HttpRequest): The incoming HTTP request.
        category_id (int): The ID of the category to edit.

    Returns:
        HttpResponse: Renders the edit category template or redirects 
                      to the category list on successful update.
    """
    if not is_admin(request.user):
        return redirect('auth.login')

    category = get_object_or_404(BlogCategory, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            updated_category = form.save(commit=False)
            updated_category.slug = slugify(updated_category.name)

            # Ensure unique name and slug (excluding current category)
            if BlogCategory.objects.filter(name=updated_category.name).exclude(id=category_id).exists():
                form.add_error('name', 'A category with this name already exists.')
            elif BlogCategory.objects.filter(slug=updated_category.slug).exclude(id=category_id).exists():
                form.add_error('name', 'A category with this slug already exists.')
            else:
                updated_category.save()
                messages.success(request, 'Category updated successfully!')
                return redirect('admin_panel:admin_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_panel/categories/edit.html', {
        'form': form,
        'category': category,
        'page_title': 'Edit Category Information'
    })




def category_delete(request, category_id):
    
    """
        Delete an existing blog category.

        Checks for admin access and deletes the specified category upon POST request.
        Displays success or error messages based on the outcome.

        Args:
            request (HttpRequest): The incoming HTTP request.
            category_id (int): ID of the category to delete.

        Returns:
            HttpResponse: Renders the delete confirmation page or redirects after deletion.

    """
   
    if not is_admin(request.user):
        return redirect('auth.login')

    category = get_object_or_404(BlogCategory, id=category_id)

    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Category deleted successfully!')
            return redirect('admin_panel:admin_categories')
        except Exception as e:
            messages.error(request, f"Error deleting category: {str(e)}")

    context = {
        'category': category,
        'page_title': 'Delete Category Confirmation'
    }

    return render(request, 'admin_panel/categories/delete.html', context)




#### End of handling of category section #####





#### Start of handling of log or error handing section #####

def error_logs(request):

    """
    Display a paginated and filterable list of application error logs.

    Supports filtering by search keyword, log level, and date range.
    Only accessible by admin users.

    Args:
        request (HttpRequest): The incoming HTTP request with optional GET parameters:
            - search (str): Text to search within message or traceback.
            - status (str): Log level to filter (info, error, debug, warning).
            - start_date (str): Filter logs from this date (inclusive).
            - end_date (str): Filter logs up to this date (inclusive).
            - page (int): Page number for pagination.

    Returns:
        HttpResponse: Renders the log list template with paginated and filtered logs.
    """
      
    if not is_admin(request.user):
        return redirect('auth.login')

    search = request.GET.get('search', '')
    level = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    logs = AppLog.objects.all().order_by('-timestamp')

    if search:
        logs = logs.filter(Q(message__icontains=search) | Q(traceback__icontains=search))
    if level:
        logs = logs.filter(level=level.upper())
    if start_date:
        logs = logs.filter(timestamp__gte=start_date)
    if end_date:
        logs = logs.filter(timestamp__lte=end_date)

    paginator = Paginator(logs, 25)
    page = request.GET.get('page')
    logs_page = paginator.get_page(page)

    status_choices = {
        'info': 'Info',
        'debug': 'Debug',
        'error': 'Error',
        'warning': 'Warning',
    }

    return render(request, 'admin_panel/log_errors/index.html', {
        'logs': logs_page,
        'search': search,
        'status': level,
        'start_date': start_date,
        'end_date': end_date,
        'page_title' : 'Error Logs List',
        'status_choices':status_choices,
    })

def error_logs_details(request, error_id):

    """
    Display the details of a specific application error log.

    Allows updating the status of the error via POST request.

    Args:
        request (HttpRequest): The incoming HTTP request.
        error_id (int): ID of the error log to retrieve and optionally update.

    Returns:
        HttpResponse: Renders the log detail template, or redirects to the logs list after update.
    """
  
    error = get_object_or_404(AppLog, id=error_id)

    if request.method == 'POST':
        new_status = request.POST.get("status")
        if new_status:
            error.status = int(new_status)
            error.save()
        return redirect('admin_panel:admin_logs')

    return render(request, 'admin_panel/log_errors/details.html', {
        'error': error,
        'page_title': 'Error details',
    })



#### End of handling of log or error handing section #####



def chatbot(request):
 
    if not is_admin(request.user):
        return redirect('auth.login')
    
    context = {
        'chatbot_status': 'online'
    }

    return render(request, 'admin_panel/chatbot/chat.html', context)


@require_http_methods(["POST"])
def send_message(request):
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Message is required'})
        
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        
        # Prepare the conversation context
        conversation = [
            {"role": "system", "content": """You are an AI assistant specialized in astrology and Kundli analysis. 
            You can help with:
            1. Analyzing Kundli reports
            2. Providing horoscope predictions
            3. Explaining astrological concepts
            4. Answering questions about subscriptions and services
            5. General astrology guidance
            
            Always maintain a professional and helpful tone. If you're unsure about something, 
            acknowledge it and suggest consulting with a professional astrologer."""},
            {"role": "user", "content": message}
        ]
        
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return JsonResponse({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def setting(request):
    if not is_admin(request.user):
        return redirect('auth.login')
    
    if request.method == 'POST':
        try:
            # Update settings
            settings = SiteSettings.objects.first()
            if not settings:
                settings = SiteSettings.objects.create()
            
            settings.site_name = request.POST.get('site_name')
            settings.site_description = request.POST.get('site_description')
            settings.contact_email = request.POST.get('contact_email')
            settings.contact_phone = request.POST.get('contact_phone')
            settings.address = request.POST.get('address')
            settings.social_facebook = request.POST.get('social_facebook')
            settings.social_twitter = request.POST.get('social_twitter')
            settings.social_instagram = request.POST.get('social_instagram')
            settings.social_youtube = request.POST.get('social_youtube')
            settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            
            settings.save()

            messages.success(request, 'Settings updated successfully.')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    context = {
        'settings': SiteSettings.objects.first(),
        'page_title' : 'Application Configuration'
    }

    return render(request, 'admin_panel/settings/index.html', context)


def generate_kundli_description(kundli_data, report_type='basic'):
    """Generate AI description for Kundli report"""
    try:
        # Initialize OpenAI client
        openai.api_key = settings.OPENAI_API_KEY
        
        # Prepare the prompt based on report type
        if report_type == 'basic':
            prompt = f"""Analyze the following Kundli report and provide a basic analysis:

Name: {kundli_data['name']}
Birth Date: {kundli_data['birth_date']}
Birth Time: {kundli_data['birth_time']}
Birth Place: {kundli_data['birth_place']}
Birth Sign: {kundli_data['birth_sign']}
Ascendant: {kundli_data['ascendant']}

Please provide:
1. A brief overview of the birth chart
2. Key planetary positions and their significance
3. Basic personality traits
4. General life path indicators
5. Simple recommendations

Keep the analysis concise and easy to understand."""
        else:
            prompt = f"""Provide a comprehensive analysis of the following Kundli report:

Name: {kundli_data['name']}
Birth Date: {kundli_data['birth_date']}
Birth Time: {kundli_data['birth_time']}
Birth Place: {kundli_data['birth_place']}
Birth Sign: {kundli_data['birth_sign']}
Ascendant: {kundli_data['ascendant']}

Planetary Positions:
{kundli_data['planetary_positions']}

Houses:
{kundli_data['houses']}

Yogas:
{kundli_data['yogas']}

Doshas:
{kundli_data['doshas']}

Please provide detailed analysis for:
1. Personality Analysis: Deep insights into character traits, strengths, and challenges
2. Career Analysis: Professional inclinations, suitable career paths, and timing
3. Relationship Analysis: Compatibility, marriage timing, and relationship dynamics
4. Health Analysis: Health indicators, potential concerns, and preventive measures
5. Financial Analysis: Wealth patterns, investment opportunities, and financial timing
6. Spiritual Analysis: Spiritual inclinations and growth potential
7. Life Periods: Major life periods and timing of significant events
8. Detailed Recommendations: Specific guidance for personal development

Format each section with clear headings and bullet points where appropriate."""

        # Get AI analysis
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert astrologer with deep knowledge of Vedic astrology and Kundli analysis. Provide detailed, accurate, and insightful analysis while maintaining a professional and helpful tone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000 if report_type == 'premium' else 1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating description: {str(e)}"

def analyze_kundli_ai(request, kundli_id):
    if not is_admin(request.user):
        return redirect('auth.login')
    
    try:
        kundli = KundliReport.objects.get(id=kundli_id)
        
        # Prepare Kundli data
        kundli_data = {
            'name': kundli.name,
            'birth_date': kundli.birth_date.strftime('%Y-%m-%d'),
            'birth_time': kundli.birth_time.strftime('%H:%M'),
            'birth_place': kundli.place,
            'birth_sign': kundli.birth_sign,
            'ascendant': kundli.ascendant,
            'planetary_positions': kundli.planetary_positions,
            'houses': kundli.houses,
            'yogas': kundli.yogas,
            'doshas': kundli.doshas
        }
        
        # Generate descriptions if not already present
        if not kundli.basic_description:
            kundli.basic_description = generate_kundli_description(kundli_data, 'basic')
        
        if not kundli.premium_description:
            kundli.premium_description = generate_kundli_description(kundli_data, 'premium')
            
            # Parse premium description into sections
            sections = kundli.premium_description.split('\n\n')
            for section in sections:
                if 'Personality Analysis:' in section:
                    kundli.personality_analysis = section.replace('Personality Analysis:', '').strip()
                elif 'Career Analysis:' in section:
                    kundli.career_analysis = section.replace('Career Analysis:', '').strip()
                elif 'Relationship Analysis:' in section:
                    kundli.relationship_analysis = section.replace('Relationship Analysis:', '').strip()
                elif 'Health Analysis:' in section:
                    kundli.health_analysis = section.replace('Health Analysis:', '').strip()
                elif 'Financial Analysis:' in section:
                    kundli.financial_analysis = section.replace('Financial Analysis:', '').strip()
                elif 'Spiritual Analysis:' in section:
                    kundli.spiritual_analysis = section.replace('Spiritual Analysis:', '').strip()
                elif 'Life Periods:' in section:
                    kundli.life_periods = section.replace('Life Periods:', '').strip()
                elif 'Recommendations:' in section:
                    kundli.recommendations = section.replace('Recommendations:', '').strip()
        
        kundli.save()
        
        context = {
            'kundli': kundli,
            'basic_description': kundli.basic_description,
            'premium_description': kundli.premium_description,
            'personality_analysis': kundli.personality_analysis,
            'career_analysis': kundli.career_analysis,
            'relationship_analysis': kundli.relationship_analysis,
            'health_analysis': kundli.health_analysis,
            'financial_analysis': kundli.financial_analysis,
            'spiritual_analysis': kundli.spiritual_analysis,
            'life_periods': kundli.life_periods,
            'recommendations': kundli.recommendations
        }
        
        return render(request, 'admin_panel/kundli/ai_analysis.html', context)
        
    except KundliReport.DoesNotExist:
        messages.error(request, 'Kundli report not found.')
        return redirect('admin_panel:admin_kundli')
    except Exception as e:
        messages.error(request, f'Error analyzing Kundli: {str(e)}')
        return redirect('admin_panel:admin_kundli')
