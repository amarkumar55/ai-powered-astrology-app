import re
import bleach
from django import forms
from subscription.models import Plan
from blogs.models import BlogPost, BlogCategory, BlogComment
from horoscope.models import Horoscope
from dasha.models import DashaEffect
from django.utils.text import slugify
from panchang.models import Panchang
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.fullmatch(r"[A-Za-z]+", name):
            raise forms.ValidationError("Name can only contain letters.")
        return bleach.clean(name, tags=[], strip=True)


    def clean_description(self):
        description = self.cleaned_data.get("description")
        if not re.fullmatch(r"[A-Za-z0-9\s,.-]+", description):
            raise forms.ValidationError("description can only contain letters.")
        return bleach.clean(description, tags=[], strip=True)
    
class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['name', 'description', 'price', 'duration_days']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not re.fullmatch(r"[A-Za-z\s]+", name):
            raise forms.ValidationError("Name can only contain letters and spaces.")
        return bleach.clean(name.strip(), tags=[], strip=True)

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description:
            if not re.fullmatch(r"[A-Za-z0-9\s,.\-()]+", description):
                raise forms.ValidationError("Description contains invalid characters.")
            return bleach.clean(description.strip(), tags=[], strip=True)
        return ""

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None or price <= 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price

    def clean_duration_days(self):
        duration = self.cleaned_data.get("duration_days")
        if duration is None or duration <= 0:
            raise forms.ValidationError("Duration must be greater than 0.")
        return duration

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'category', 'content', 'excerpt',
            'featured_image', 'status', 'meta_title', 'meta_description', 'tags'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g. django, python'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not re.fullmatch(r"[A-Za-z0-9\s,.'\"!?-]+", title):
            raise forms.ValidationError("Title contains invalid characters.")
        return bleach.clean(title.strip(), tags=[], strip=True)

    def clean_excerpt(self):
        excerpt = self.cleaned_data.get("excerpt")
        if excerpt and not re.fullmatch(r"[A-Za-z0-9\s,.'\"!?-]+", excerpt):
            raise forms.ValidationError("Excerpt contains invalid characters.")
        return bleach.clean(excerpt.strip(), tags=[], strip=True)

    def clean_meta_title(self):
        meta_title = self.cleaned_data.get("meta_title")
        if meta_title and len(meta_title) > 200:
            raise forms.ValidationError("Meta title is too long.")
        return bleach.clean(meta_title.strip(), tags=[], strip=True)

    def clean_meta_description(self):
        meta_description = self.cleaned_data.get("meta_description")
        return bleach.clean(meta_description.strip(), tags=[], strip=True)

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        if tags and not re.fullmatch(r"[A-Za-z0-9,\s-]+", tags):
            raise forms.ValidationError("Tags can only contain letters, numbers, commas, and hyphens.")
        return bleach.clean(tags.strip(), tags=[], strip=True)

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        return slugify(slug)

    def clean_content(self):
        content = self.cleaned_data.get("content")
        # Allow safe HTML for RichTextField but still clean potentially dangerous scripts
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'blockquote']
        allowed_attrs = {'a': ['href', 'title'], 'img': ['src', 'alt']}
        return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    
class HoroscopeForm(forms.ModelForm):
    class Meta:
        model = Horoscope
        fields = ['sign', 'date', 'type', 'general', 'love', 'career', 'health', 'finance']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'general': forms.Textarea(attrs={'rows': 3}),
            'love': forms.Textarea(attrs={'rows': 3}),
            'career': forms.Textarea(attrs={'rows': 3}),
            'health': forms.Textarea(attrs={'rows': 3}),
            'finance': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_sign(self):
        sign = self.cleaned_data.get("sign")
        if not re.fullmatch(r"[A-Za-z\s]+", sign):
            raise forms.ValidationError("Sign can only contain letters and spaces.")
        return bleach.clean(sign.strip(), tags=[], strip=True)

    def _clean_text_field(self, field_value, field_name):
        # Shared cleaner for general, love, etc.
        if field_value:
            if len(field_value) < 10:
                raise forms.ValidationError(f"{field_name.capitalize()} must be at least 10 characters.")
            allowed_tags = ['strong', 'em', 'b', 'i', 'p', 'br']
            return bleach.clean(field_value.strip(), tags=allowed_tags, strip=True)
        return ""

    def clean_general(self):
        return self._clean_text_field(self.cleaned_data.get("general"), "general")

    def clean_love(self):
        return self._clean_text_field(self.cleaned_data.get("love"), "love")

    def clean_career(self):
        return self._clean_text_field(self.cleaned_data.get("career"), "career")

    def clean_health(self):
        return self._clean_text_field(self.cleaned_data.get("health"), "health")

    def clean_finance(self):
        return self._clean_text_field(self.cleaned_data.get("finance"), "finance")
    
class DashaEffectForm(forms.ModelForm):
    class Meta:
        model = DashaEffect
        fields = [
            'mahadasha_planet', 'antar_dasha_planet',
            'start_date', 'end_date',
            'mahadasha_effect', 'antardasha_effect', 'combined_effect'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'mahadasha_effect': forms.Textarea(attrs={'rows': 3}),
            'antardasha_effect': forms.Textarea(attrs={'rows': 3}),
            'combined_effect': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_mahadasha_planet(self):
        value = self.cleaned_data.get("mahadasha_planet")
        if not re.fullmatch(r"[A-Za-z\s]+", value):
            raise forms.ValidationError("Mahadasha planet can only contain letters and spaces.")
        return bleach.clean(value.strip(), tags=[], strip=True)

    def clean_antar_dasha_planet(self):
        value = self.cleaned_data.get("antar_dasha_planet")
        if not re.fullmatch(r"[A-Za-z\s]+", value):
            raise forms.ValidationError("Antardasha planet can only contain letters and spaces.")
        return bleach.clean(value.strip(), tags=[], strip=True)

    def _clean_effect_field(self, value, field_name):
        if value:
            if len(value) < 10:
                raise forms.ValidationError(f"{field_name.capitalize()} must be at least 10 characters.")
            allowed_tags = ['strong', 'em', 'p', 'br']
            return bleach.clean(value.strip(), tags=allowed_tags, strip=True)
        return ""

    def clean_mahadasha_effect(self):
        return self._clean_effect_field(self.cleaned_data.get("mahadasha_effect"), "Mahadasha effect")

    def clean_antardasha_effect(self):
        return self._clean_effect_field(self.cleaned_data.get("antardasha_effect"), "Antardasha effect")

    def clean_combined_effect(self):
        return self._clean_effect_field(self.cleaned_data.get("combined_effect"), "Combined effect")

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("End date cannot be earlier than start date.")

class PanchangForm(forms.ModelForm):
    class Meta:
        model = Panchang
        fields = [
            'date', 'tithi', 'vara', 'nakshatra', 'yoga',
            'karana', 'sunrise', 'sunset', 'rahu_kaal',
            'gulika_kaal', 'yamaganda','abhijit_muhurat'
        ]

    def clean_tithi(self):
        tithi = self.cleaned_data.get("tithi")
        if tithi and not re.fullmatch(r"[A-Za-z0-9\s\-]+", tithi):
            raise forms.ValidationError("Tithi contains invalid characters.")
        return bleach.clean(tithi.strip(), tags=[], strip=True)
    
    def clean_vara(self):
        vara = self.cleaned_data.get("vara")
        if vara and not re.fullmatch(r"[A-Za-z0-9\s\-]+", vara):
            raise forms.ValidationError("Vara contains invalid characters.")
        return bleach.clean(vara.strip(), tags=[], strip=True)

    def clean_nakshatra(self):
        nakshatra = self.cleaned_data.get("nakshatra")
        if nakshatra and not re.fullmatch(r"[A-Za-z0-9\s\-]+", nakshatra):
            raise forms.ValidationError("Nakshatra contains invalid characters.")
        return bleach.clean(nakshatra.strip(), tags=[], strip=True)

    def clean_yoga(self):
        yoga = self.cleaned_data.get("yoga")
        if yoga and not re.fullmatch(r"[A-Za-z0-9\s\-]+", yoga):
            raise forms.ValidationError("Yoga contains invalid characters.")
        return bleach.clean(yoga.strip(), tags=[], strip=True)

    def clean_karana(self):
        karana = self.cleaned_data.get("karana")
        if karana and not re.fullmatch(r"[A-Za-z0-9\s\-]+", karana):
            raise forms.ValidationError("Karana contains invalid characters.")
        return bleach.clean(karana.strip(), tags=[], strip=True)
    
    def clean_rahu_kaal(self):
        rahu_kaal = self.cleaned_data.get("rahu_kaal")
        if rahu_kaal and not re.fullmatch(r"[A-Za-z0-9\s\-]+", rahu_kaal):
            raise forms.ValidationError("Rahu kaal contains invalid characters.")
        return bleach.clean(rahu_kaal.strip(), tags=[], strip=True)
    
    def clean_gulika_kaal(self):
        gulika_kaal = self.cleaned_data.get("gulika_kaal")
        if gulika_kaal and not re.fullmatch(r"[A-Za-z0-9\s\-]+", gulika_kaal):
            raise forms.ValidationError("Gulika kaal contains invalid characters.")
        return bleach.clean(gulika_kaal.strip(), tags=[], strip=True)
    
    def clean_yamaganda(self):
        yamaganda = self.cleaned_data.get("yamaganda")
        if yamaganda and not re.fullmatch(r"[A-Za-z0-9\s\-]+", yamaganda):
            raise forms.ValidationError("Yamaganda contains invalid characters.")
        return bleach.clean(yamaganda.strip(), tags=[], strip=True)
    

    def clean_abhijit_muhurat(self):
        abhijit_muhurat = self.cleaned_data.get("abhijit_muhurat")
        if abhijit_muhurat and not re.fullmatch(r"[A-Za-z0-9\s\-]+", abhijit_muhurat):
            raise forms.ValidationError("Abhijit muhurat contains invalid characters.")
        return bleach.clean(abhijit_muhurat.strip(), tags=[], strip=True)
    
    
    def clean(self):
        cleaned_data = super().clean()
        sunrise = cleaned_data.get('sunrise')
        sunset = cleaned_data.get('sunset')

        if sunrise and sunset:
            if sunrise >= sunset:
                raise ValidationError("Sunrise must be earlier than sunset.")
        
        return cleaned_data
