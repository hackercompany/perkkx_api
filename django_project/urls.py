from django.conf.urls import patterns, include, url
from django_project.api import userApi, dealsApi, merchantApi,redeemCoupon, profileApi, ratingApi, webPortal,search
from django_project.merchantApi import getApi, postApi
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

url(r'^text',redeemCoupon.test,name='redeemCoupon.test'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^perkkx/user/coupon/(?P<uid>\w+)', userApi.user_coupons, name='userApi.user_coupons'),
    url(r'^perkkx/signup', userApi.signup, name='userApi.signup'),
    url(r'^perkkx/user', userApi.getdata, name='userApi.getdata'),
    
    url(r'^perkkx/update/user',userApi.updateuser, name='userApi.updateuser'),
    url(r'^perkkx/check', userApi.user_exist, name="userApi.user_exist"),
    url(r'^perkkx/echo', 'preks.echo'),
    url(r'^perkkx/verifyUser/(?P<code>\w+)', userApi.verifyUser, name='userApi.verifyUser'),
    url(r'^perkkx/deals/all/(?P<vendor>\d+)', dealsApi.get_all_deals_for_vendor, name='dealsApi.get_all_deals_for_vendor'),
    url(r'^perkkx/deals/onetime', dealsApi.get_one_time_deals, name='dealsApi.get_one_time_deals'),
    url(r'^perkkx/deals/(?P<category>\d+)', dealsApi.get_deals, name='dealsApi.get_deals'),
    url(r'^perkkx/deals', dealsApi.get_totals, name='dealsApi.get_totals'),
    url(r'^perkkx/getcompany', userApi.getFacility, name='userApi.getFacility'),
    url(r'^perkkx/redeem/check', redeemCoupon.check_coupon, name='redeemCoupon.check_coupon'),
    url(r'^perkkx/redeem', redeemCoupon.add_coupon, name='redeemCoupon.add_coupon'),
    url(r'^perkkx/ecom/redeem', redeemCoupon.get_ecom_coupon, name='redeemCoupon.get_ecom_coupon'),

    url(r'^perkkx/merchant/(?P<user>\w+)/(?P<vendor>\d+)', merchantApi.merchants, name='merchantApi.merchant'),
    url(r'^perkkx/mfollow/(?P<user>\w+)/(?P<vendor>\d+)', userApi.fMerchant, name='userApi.fMerchant'),
    url(r'^perkkx/donemerchant/(?P<rowID>\w+)', webPortal.addData, name='webPortal.addData'),
    url(r'^perkkx/profile/savings/(?P<userID>\w+)', profileApi.get_savings, name='profileApi.get_savings'),
    url(r'^perkkx/profile/followed/(?P<userID>\w+)', profileApi.get_followed, name='profileApi.get_followed'),
    url(r'^perkkx/profile/rate', ratingApi.rate_merchant, name='ratingApi.rate_merchant'),
    url(r'^perkkx/profile/check', profileApi.pre_app_check, name='profileApi.pre_app_check'),
    url(r'^perkkx/profile/ratings', ratingApi.get_ratings, name='ratingApi.get_ratings'),
    url(r'^perkkx/profile/suggest', profileApi.suggest_merchant, name='profileApi.suggest_merchant'),

    url(r'^perkkx/merchantapp/validate', getApi.validate_code, name='getApi.validate_code'),
    url(r'^perkkx/merchantapp/login', postApi.login, name='postApi.login'),
    url(r'^perkkx/merchantapp/signup', postApi.signup, name='postApi.signup'),      # Not to be used by app
    url(r'^perkkx/merchantapp/submit/(?P<vendor_id>\d+)', postApi.post, name='postApi.post'),
    url(r'^perkkx/merchantapp/count/(?P<vendor_id>\d+)', getApi.get_count, name='getApi.get_count'),
    url(r'^perkkx/merchantapp/(?P<typ>\w+)/(?P<vendor_id>\d+)', getApi.get, name='getApi.get'),
    url(r'^perkkx/search', search.search, name='search.search'),

    url(r'^wadi/', include('wadi.urls')),
    url(r'^manoj/', include('manoj.urls'))

)
