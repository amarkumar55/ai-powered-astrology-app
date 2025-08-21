class DBRouterManager:

    shared_apps = {
        'auth',
        'authtoken',
        'contenttypes',
        'admin',
        'sessions',
        'messages',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'social_django',
        'django_otp',
        'django_otp.plugins.otp_static',
        'django_otp.plugins.otp_totp',
        'compressor',
        'phonenumber_field',
        'django_ratelimit',
        'csp',
        'fontawesomefree',
        'ckeditor',
        'rest_framework',
    }

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'astrology':
            return 'default'
        elif model._meta.app_label == 'smartnotes':
            return 'smartnotes'
        elif model._meta.app_label == 'core':
            return hints.get('default','smartnotes')  # dynamic
        elif model._meta.app_label in self.shared_apps:
            return hints.get('default','smartnotes')
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'astrology':
            return 'default'
        elif model._meta.app_label == 'smartnotes':
            return 'smartnotes'
        elif model._meta.app_label == 'core':
            return hints.get('default','smartnotes')  # dynamic
        elif model._meta.app_label in self.shared_apps:
            return hints.get('default', 'smartnotes')
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'astrology':
            return db == 'default'
        elif app_label in self.shared_apps:
            return db in ['default', 'smartnotes']
        elif app_label == 'core':
            return db in ['default', 'smartnotes']
        elif app_label in self.shared_apps:
            return db in ['default', 'smartnotes']
        return None