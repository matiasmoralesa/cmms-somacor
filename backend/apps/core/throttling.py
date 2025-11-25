"""
Custom throttling classes for rate limiting
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst requests - allows short bursts of activity
    Rate: 10 requests per minute
    """
    scope = 'burst'
    rate = '10/min'


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained requests - limits overall request rate
    Rate: 100 requests per minute
    """
    scope = 'sustained'
    rate = '100/min'


class DailyRateThrottle(UserRateThrottle):
    """
    Throttle for daily requests - limits total daily requests
    Rate: 10000 requests per day
    """
    scope = 'daily'
    rate = '10000/day'


class WebhookRateThrottle(UserRateThrottle):
    """
    Throttle for webhook creation/testing
    Rate: 30 requests per hour
    """
    scope = 'webhook'
    rate = '30/hour'


class ReportGenerationThrottle(UserRateThrottle):
    """
    Throttle for report generation (expensive operations)
    Rate: 10 requests per hour
    """
    scope = 'report'
    rate = '10/hour'


class FileUploadThrottle(UserRateThrottle):
    """
    Throttle for file uploads
    Rate: 50 requests per hour
    """
    scope = 'upload'
    rate = '50/hour'


class AnonStrictRateThrottle(AnonRateThrottle):
    """
    Strict throttle for anonymous users
    Rate: 5 requests per minute
    """
    scope = 'anon_strict'
    rate = '5/min'
