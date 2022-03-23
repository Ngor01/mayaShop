from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.http import HttpResponse
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return  cart
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id = product_id)
    #if the user the is authenticate
    if current_user.is_authenticated:
        product_variation =[]
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_items:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            # print(ex_var_list)

            if product_variation in ex_var_list:
                #increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity+=1
                item.save()

            else:
                items =CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    items.variations.clear()
                    items.variations.add(*product_variation)
                items.save()
        else:
            cart_items = CartItem.objects.create(
                product = product,
                quantity = 1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_items.variations.clear()
                cart_items.variations.add(*product_variation)
            cart_items.save()
        return redirect('cart')

    else:
        product_variation =[]
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
             #get the cart using the card_id present in the session
        except  Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            #existing variations ->db
            #current variations ->product_variation
            #item_id -> db
            ex_var_list = []
            id = []
            for item in cart_items:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)

            if product_variation in ex_var_list:
                #increase cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity+=1
                item.save()

            else:
                items =CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    items.variations.clear()
                    items.variations.add(*product_variation)
                items.save()
        else:
            cart_items = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_items.variations.clear()
                cart_items.variations.add(*product_variation)
            cart_items.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_items_id):
    product = get_object_or_404(Product, id = product_id)
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.get(product = product, user=request.user, id = cart_items_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.get(product = product, cart=cart, id = cart_items_id)
        if cart_items.quantity >1:
            cart_items.quantity -=1
            cart_items.save()
        else:
            cart_items.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_items_id):
    product = get_object_or_404(Product, id = product_id)
    if request.user.is_authenticated:
        cart_items = CartItem.objects.get(product = product, user=request.user, id=cart_items_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.get(product = product, cart = cart, id=cart_items_id)
    cart_items.delete()
    return redirect('cart')

def cart(request, total = 0, quantity = 0, cart_item = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_items in cart_item:
            total +=(cart_items.product.price * cart_items.quantity)
            quantity += cart_items.quantity
        tax = (2 * total) /100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
    'total': total,
    'quantity': quantity,
    'cart_item': cart_item,
    'tax': tax,
    'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)
@login_required(login_url='login')
def checkout(request, total = 0, quantity = 0, cart_item = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_item = CartItem.objects.filter(user=request.user, is_active = True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.filter(cart=cart, is_active = True)
        for cart_items in cart_item:
            total +=(cart_items.product.price * cart_items.quantity)
            quantity += cart_items.quantity
        tax = (2 * total) /100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
    'total': total,
    'quantity': quantity,
    'cart_item': cart_item,
    'tax': tax,
    'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
