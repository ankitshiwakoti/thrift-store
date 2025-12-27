from django.contrib.admin.views.decorators import staff_member_required
from .models import Category, Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import Cart, CartItem, Product
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CartItem, Order, OrderItem


@staff_member_required
def admin_dashboard(request):
    total_products = Product.objects.count()
    available_products = Product.objects.filter(status="AVAILABLE").count()
    sold_products = Product.objects.filter(status="SOLD").count()
    total_categories = Category.objects.count()

    context = {
        "total_products": total_products,
        "available_products": available_products,
        "sold_products": sold_products,
        "total_categories": total_categories,
    }
    return render(request, "store/admin/dashboard.html", context)


@staff_member_required
def admin_products(request):
    products = Product.objects.select_related("category").order_by("-id")
    return render(request, "store/admin/products.html", {"products": products})


@staff_member_required
def admin_categories(request):
    categories = Category.objects.order_by("name")
    return render(request, "store/admin/categories.html", {"categories": categories})

@staff_member_required
def admin_add_category(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            Category.objects.create(name=name, description=description)
            return redirect("admin_categories")

    return render(request, "store/admin/add_category.html")

@staff_member_required
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.name = request.POST.get("name", "").strip()
        category.description = request.POST.get("description", "").strip()
        category.save()
        return redirect("admin_categories")

    return render(
        request,
        "store/admin/edit_category.html",
        {"category": category},
    )


@staff_member_required
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.delete()
        return redirect("admin_categories")

    return render(
        request,
        "store/admin/delete_category.html",
        {"category": category},
    )



@staff_member_required
def admin_add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price")
        description = request.POST.get("description", "").strip()
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        if name and price and category_id:
            Product.objects.create(
                name=name,
                price=price,
                description=description,
                category_id=category_id,
                image=image,
                status="AVAILABLE",
            )
            return redirect("admin_products")

    return render(
        request,
        "store/admin/add_product.html",
        {"categories": categories},
    )
@staff_member_required
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name", "").strip()
        product.price = request.POST.get("price")
        product.description = request.POST.get("description", "").strip()
        product.category_id = request.POST.get("category")
        product.status = request.POST.get("status")

        image = request.FILES.get("image")
        if image:
            product.image = image

        product.save()
        return redirect("admin_products")

    return render(
        request,
        "store/admin/edit_product.html",
        {
            "product": product,
            "categories": categories,
        },
    )


@staff_member_required
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("admin_products")

    return render(
        request,
        "store/admin/delete_product.html",
        {"product": product},
    )


# Public Store Views

def home(request):
    q = request.GET.get("q", "").strip()

    categories = Category.objects.order_by("name")

    featured_products = Product.objects.filter(status="AVAILABLE").order_by("-id")[:8]

    # Optional: if user searches from home
    search_results = []
    if q:
        search_results = Product.objects.filter(
            status="AVAILABLE"
        ).filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        ).order_by("-id")

    return render(
        request,
        "store/public/home.html",
        {
            "categories": categories,
            "featured_products": featured_products,
            "q": q,
            "search_results": search_results,
        },
    )


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, status="AVAILABLE").order_by("-id")
    return render(
        request,
        "store/public/category_products.html",
        {"category": category, "products": products},
    )


# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id, status="AVAILABLE")
#     categories = Category.objects.order_by("name")
#     return render(request, "store/public/product_detail.html", {"product": product,"categories": categories})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.order_by("name")

    related_products = Product.objects.filter(
        category=product.category,
        status="AVAILABLE"
    ).exclude(id=product.id).order_by("-id")[:4]

    return render(request, "store/public/product_detail.html", {
        "product": product,
        "categories": categories,
        "related_products": related_products,
    })


from django.db.models import Q
from .models import Product, Category

def shop(request):
    categories = Category.objects.order_by("name")

    q = request.GET.get("q", "").strip()
    cat_id = request.GET.get("cat", "").strip()
    sort = request.GET.get("sort", "new")  # new | price_asc | price_desc | name

    products = Product.objects.all()

    # Optional: only show available on public pages
    products = products.filter(status="AVAILABLE")

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )

    if cat_id.isdigit():
        products = products.filter(category_id=int(cat_id))

    if sort == "price_asc":
        products = products.order_by("price", "-id")
    elif sort == "price_desc":
        products = products.order_by("-price", "-id")
    elif sort == "name":
        products = products.order_by("name")
    else:  # "new"
        products = products.order_by("-id")

    return render(request, "store/public/shop.html", {
        "categories": categories,
        "products": products,
        "q": q,
        "cat_id": cat_id,
        "sort": sort,
        "total": products.count(),
    })



def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not password1:
            messages.error(request, "Username and password are required.")
            return redirect("register")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created! Please login.")
        return redirect("login")

    return render(request, "store/public/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "store/public/login.html")




def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def cart_detail(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product", "product__category").all()
    return render(request, "store/public/cart.html", {"cart": cart, "items": items})

@login_required
def cart_add(request, product_id):
    if request.method != "POST":
        return redirect("product_detail", product_id=product_id)

    product = get_object_or_404(Product, id=product_id, status="AVAILABLE")
    cart = _get_cart(request.user)

    # Add only once (thrift logic)
    CartItem.objects.get_or_create(cart=cart, product=product)

    messages.success(request, f"{product.name} added to cart.")
    return redirect(request.POST.get("next") or "cart_detail")


@login_required
def cart_update(request, item_id):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = _get_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    qty = request.POST.get("quantity", "1")
    try:
        qty = int(qty)
    except ValueError:
        qty = 1

    if qty <= 0:
        item.delete()
        messages.info(request, "Item removed.")
    else:
        item.quantity = qty
        item.save()
        messages.success(request, "Cart updated.")

    return redirect("cart_detail")

@login_required
def cart_remove(request, item_id):
    if request.method != "POST":
        return redirect("cart_detail")

    cart = _get_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("cart_detail")



from django.db import transaction
from .models import Order, OrderItem, Cart

@login_required
def checkout(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product").all()

    if not items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("cart_detail")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not full_name or not phone or not address:
            messages.error(request, "Please fill in name, phone and address.")
            return redirect("checkout")

        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=address,
                notes=notes,
                total_amount=cart.total_price,
                status="PLACED",
            )

            # Create order items + mark products SOLD
            for it in items:
                OrderItem.objects.create(
                    order=order,
                    product=it.product,
                    price=it.product.price,
                    quantity=1,
                )

                it.product.status = "SOLD"
                it.product.save()

            # Clear cart
            cart.items.all().delete()

        messages.success(request, f"Order placed successfully! Order #{order.id}")
        return redirect("order_success", order_id=order.id)

    # GET request
    return render(request, "store/public/checkout.html", {
        "cart": cart,
        "items": items,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/public/order_success.html", {"order": order})



@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/public/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items", "items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "store/public/order_detail.html", {"order": order})
