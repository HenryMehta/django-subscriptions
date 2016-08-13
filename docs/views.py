from django.shortcuts import render
from datetime import date
from subscriptions.models import *
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

@login_required
def home (request):        
    subs = MySubs.objects.filter(user=request.user).order_by('-sub__start_date','sub__end_date','sub__name')
    return render(request, 'subscriptions/my_subscriptions.html',
                  {'mysubs_list' : subs,})

def list (request):
    subs = Subscription.objects.filter(end_date__gte = date.today()).order_by('start_date','-end_date','name')
    return render(request, 'subscriptions/list_subscriptions.html',
                  {'subscription_list' : subs,}
                  )

@login_required
def add (request, sid="0"):
    if request.method == "GET":
        if sid == 0:
            #No subscription id passed through so error
            subs = Subscription.objects.filter(end_date__gte = date.today()).order_by('start_date','-end_date','name')
            return render(request, 'subscriptions/list_subscriptions.html',
                          {'subscription_list' : subs,}
                          )
        else:
            subs = Subscription.objects.get(id=int(sid))
            cats = SubscriptionCategory.objects.filter(subscription__id=int(sid))
            members = []
            for c in cats:
                if c.category.user_link == 'No-link':
                    members.append(c.category.object_list().order_by('last_name','first_name'))
                else:
                    myfilter = c.category.content_type.model+'__in'
                    members.append(User.objects.filter(**{myfilter: c.category.object_list()}).order_by('last_name','first_name'))
            z = zip(cats,members)
            return render(request, 'subscriptions/add_subscriptions.html',
                          {'subscription' : subs,
                           'zip' : z,}
                          )
    else:
        subs = Subscription.objects.get(id=int(sid))
        cats = SubscriptionCategory.objects.filter(subscription__id=int(sid))
        members = []
        for c in cats:
            if int(request.POST.get('select'+str(c.id))) != 0:
                members.append(User.objects.get(id=int(request.POST.get('select'+str(c.id)))))
        return render(request, 'subscriptions/confirm_subscriptions.html',
                      {'subscription' : subs,
                       'amount_due' : subs.cost*100,
                       'stripe_key' : settings.STRIPE_PUBLISH_KEY,
                       'members' : members}
                      )

@login_required
def detail (request, sid="0"):
    if request.method == "GET":
        if sid == "0":
            #No subscription id passed through so error
            subs = Subscription.objects.filter(end_date__gte = date.today()).order_by('start_date','-end_date','name')
            return render(request, 'subscriptions/list_subscriptions.html',
                          {'subscription_list' : subs,}
                          )
        else:
            subs = MySubs.objects.filter(token=sid)
            subscription = Subscription.objects.filter(mysubs__token=sid)[0]
            return render(request, 'subscriptions/detail_subscriptions.html',
                          {'subs' : subs,
                           'subscription' : subscription,}
                          )

@login_required        
@csrf_exempt
def process_payment(request, sid='0', count='0'):
    subs = Subscription.objects.get(id=int(sid))
    total_fee = subs.cost
    
    stripe.api_key = settings.STRIPE_API_KEY
    token = request.POST['stripeToken']
    
    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        charge = stripe.Charge.create(
            amount=int(total_fee*100), # amount in pence
            currency="gbp",
            source=token,
            description= settings.SUBSCRIPTIONS_SITE_NAME + subs.name,
      )
    except stripe.error.CardError, e:
        # The card has been declined
        return render(request, 'subscriptions/payment_declined.html',
                      {'e' : e})
    
    for x in range(1, int(count)+1):
        m = MySubs (
            user = User.objects.get(id=int(request.POST.get('user'+str(x)))),
            sub = subs,
            token = token,
            paid = False
        )
        if m.user == request.user: m.paid = True
        m.save()
    
    #send confirmation email
    msg = render_to_string('subscriptions/confirm_email.txt',
                           {'user': request.user,
                            'subscription' : subs,
                            'subs': MySubs.objects.filter(token=m.token),
                            'site_name' : settings.SUBSCRIPTIONS_SITE_NAME,
                            'total_fee' : total_fee})
    
    email = EmailMessage(settings.SUBSCRIPTIONS_SITE_NAME+ " subscription payment",
                         msg,
                         to=[request.user.email])
    email.send()

    return render(request, 'subscriptions/payment_confirmed.html')
