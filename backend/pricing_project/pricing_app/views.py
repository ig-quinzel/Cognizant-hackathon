from django.shortcuts import render

# Create your views here.
"""from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

# check if user is superuser
def superuser_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func

@login_required
@superuser_required
def dashboard(request):
    return render(request, "pricing_app/dashboard.html")"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SuperUserLoginForm

def superuser_login(request):
    if request.method == 'POST':
        form = SuperUserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SuperUserLoginForm()
    return render(request, 'pricing_app/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'pricing_app/dashboard.html')



from django.shortcuts import render
from .forms import PricePredictionForm
from .ml.predictor import predict_price

"""def quote_form(request):
    if request.method == "POST":
        form = PricePredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            predicted_price = predict_price(data)
            return render(request, "pricing_app/quote_result.html", {
                "predicted_price": predicted_price,
                "input_data": data
            })
    else:
        form = PricePredictionForm()
    return render(request, "pricing_app/quote_form.html", {"form": form})"""

"""def quote_form(request):
    if request.method == "POST":
        form = PricePredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            predicted_price = predict_price(data)

            # 🔹 Save result + input in session for use in quote_description
            request.session["prediction_result"] = {
                "data": data,
                "predicted_price": predicted_price,
            }

            return render(request, "pricing_app/quote_result.html", {
                "predicted_price": predicted_price,
                "input_data": data
            })
    else:
        form = PricePredictionForm()
    return render(request, "pricing_app/quote_form.html", {"form": form})"""

##from django.shortcuts import render, redirect
#from .forms import PricePredictionForm
#from .ml.predictor import predict_price

def quote_form(request):
    if request.method == "POST":
        form = PricePredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            predicted_price = predict_price(data)

            # --- Fix: prepare session data ---
            session_data = data.copy()

            # Convert date object to string for JSON serialization
            if "date" in session_data and hasattr(session_data["date"], "isoformat"):
                session_data["date"] = session_data["date"].isoformat()

            # Ensure predicted_price is a float (not numpy type)
            request.session["prediction_result"] = {
                "data": session_data,
                "predicted_price": float(predicted_price),
            }

            # Redirect to result page
            return render(request, "pricing_app/quote_result.html", {
                "predicted_price": predicted_price,
                "input_data": data
            })
    else:
        form = PricePredictionForm()
    return render(request, "pricing_app/quote_form.html", {"form": form})



"""def quote_description(request):
    if request.method == "POST":
        form = PricePredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            predicted_price = predict_price(data)

            # Compute competitor price (example calculation)
            competitor_price = data['competitor_price_index'] * data['sales_revenue']

            # Prepare chart data
            chart_data = {
                "predicted_price": predicted_price,
                "competitor_price": competitor_price,
                "discount_percentage": data['discount_percentage'],
                "holiday_season": int(data['holiday_season']),
                "promotion_applied": int(data['promotion_applied']),
                "sales_units": data['sales_units'],
                "economic_index": data['economic_index'],
                "weather_impact": data['weather_impact'],
            }

            return render(request, "pricing_app/quote_description.html", {
                "predicted_price": predicted_price,
                "input_data": data,
                "chart_data": chart_data,
            })
    else:
        form = PricePredictionForm()
    return render(request, "pricing_app/quote_form.html", {"form": form})"""

def quote_description(request):
    session_data = request.session.get("prediction_result")

    if not session_data:
        # If user directly visits without prediction, go back
        return redirect("quote_form")

    data = session_data["data"]
    predicted_price = session_data["predicted_price"]

    # Compute competitor price (example calculation)
    competitor_price = data['competitor_price_index'] * data['sales_revenue']

    # Prepare chart data
    chart_data = {
        "predicted_price": predicted_price,
        "competitor_price": competitor_price,
        "discount_percentage": data['discount_percentage'],
        "holiday_season": int(data['holiday_season']),
        "promotion_applied": int(data['promotion_applied']),
        "sales_units": data['sales_units'],
        "economic_index": data['economic_index'],
        "weather_impact": data['weather_impact'],
    }

    return render(request, "pricing_app/quote_description.html", {
        "predicted_price": predicted_price,
        "input_data": data,
        "chart_data": chart_data,
    })

