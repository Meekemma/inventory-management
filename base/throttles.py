from rest_framework.throttling import ScopedRateThrottle


class LoginThrottle(ScopedRateThrottle):
    scope = 'login'



class RegisterThrottle(ScopedRateThrottle):
    scope = 'register'



class LogoutThrottle(ScopedRateThrottle):
    scope = 'logout'



class ChangePasswordThrottle(ScopedRateThrottle):
    scope = 'change_password'



class UpdateProfileThrottle(ScopedRateThrottle):
    scope = 'update_profile'
