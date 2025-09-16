from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import shap
import numpy as np
from weather_utils import get_weather_data
from validators import validate_district

app = Flask(__name__, static_folder="static", template_folder="templates")
pipeline = joblib.load("model/yield_prediction_model.pkl")


model = pipeline.named_steps["model"]
preprocessor = pipeline[:-1]   
explainer = shap.TreeExplainer(model)

CROP_DATA = {
    "Rice": {"msp_per_quintal": 2300, "water_req_mm": 1300},
    "Wheat": {"msp_per_quintal": 2275, "water_req_mm": 550},
    "Maize": {"msp_per_quintal": 2225, "water_req_mm": 650},
    "Sugarcane": {"msp_per_quintal": 340, "water_req_mm": 2000},
    "Cotton": {"msp_per_quintal": 7121, "water_req_mm": 800},
    "Soyabean": {"msp_per_quintal": 4892, "water_req_mm": 600},
    "Pigeonpea": {"msp_per_quintal": 7550, "water_req_mm": 450},
    "Chickpea": {"msp_per_quintal": 5440, "water_req_mm": 400},
    "Rapeseed & Mustard": {"msp_per_quintal": 5650, "water_req_mm": 350},
    "Groundnut": {"msp_per_quintal": 6783, "water_req_mm": 600},
    "Sunflower": {"msp_per_quintal": 7280, "water_req_mm": 650},
    "Barley": {"msp_per_quintal": 1850, "water_req_mm": 350},
    "Pearl Millet": {"msp_per_quintal": 2625, "water_req_mm": 300},
    "Kharif Sorghum": {"msp_per_quintal": 3371, "water_req_mm": 500},
    "Rabi Sorghum": {"msp_per_quintal": 3371, "water_req_mm": 400},
    "Castor": {"msp_per_quintal": 7515, "water_req_mm": 450},
    "Finger Millet": {"msp_per_quintal": 4290, "water_req_mm": 400},
    "Linseed": {"msp_per_quintal": 5650, "water_req_mm": 350},
    "Safflower": {"msp_per_quintal": 5800, "water_req_mm": 300},
    "Sesamum": {"msp_per_quintal": 9267, "water_req_mm": 400},
    "Onion": {"msp_per_quintal": 2000, "water_req_mm": 450},
    "Potatoes": {"msp_per_quintal": 1500, "water_req_mm": 600},
}


def get_recommendations(district, year, area_ha, weather_data, user_crop):
    
    all_recommendations = []
    
    for crop, data in CROP_DATA.items():
        if crop.lower() == user_crop.lower():
            continue

        features = {
            "Year": year, "Area (1000 ha)": area_ha / 1000,
            "temp_avg": weather_data["temp_avg"], "temp_max": weather_data["temp_max"],
            "temp_min": weather_data["temp_min"], "humidity": weather_data["humidity"],
            "rainfall": weather_data["rainfall"], "Dist Name": district.lower(),
            "Crop": crop.upper()
        }
        features_df = pd.DataFrame([features])
        predicted_yield = pipeline.predict(features_df)[0]
        msp = data["msp_per_quintal"]
        water_req = data["water_req_mm"]
        
        estimated_revenue = (predicted_yield / 100) * msp
        irrigation_needed = max(0, water_req - weather_data["rainfall"])

        all_recommendations.append({
            "crop": crop,
            "yield": round(float(predicted_yield), 2),
            "revenue": round(float(estimated_revenue), 2),
            "irrigation": round(float(irrigation_needed), 2)
        })

    sorted_recs = sorted(all_recommendations, key=lambda x: x["revenue"], reverse=True)
    return sorted_recs[:3]


def get_shap_explanation(features_df):
    
    X_transformed = preprocessor.transform(features_df)
    shap_values = explainer(X_transformed)

    vals = shap_values.values[0]
    feat_names = preprocessor.get_feature_names_out()

    top_idx = np.argsort(np.abs(vals))[-3:][::-1]
    explanation = [
        {"feature": feat_names[i],
         "impact": round(float(vals[i]), 3),
         "direction": "increased" if vals[i] > 0 else "reduced"}
        for i in top_idx
    ]
    return explanation


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        district_input = request.form.get("district", "")
        crop_input = request.form.get("crop", "")
        year = int(request.form.get("year", 2025))
        area = float(request.form.get("area", 1.0))

        district_for_processing = district_input.lower()
        crop_for_processing = crop_input.upper()

        if not validate_district(district_for_processing):
            return jsonify({"error": "Enter a valid district"})

        weather_data = get_weather_data(district_for_processing, year)

        features = {
            "Year": year, "Area (1000 ha)": area,
            "temp_avg": weather_data["temp_avg"], "temp_max": weather_data["temp_max"],
            "temp_min": weather_data["temp_min"], "humidity": weather_data["humidity"],
            "rainfall": weather_data["rainfall"], "Dist Name": district_for_processing,
            "Crop": crop_for_processing
        }
        features_df = pd.DataFrame([features])
        predicted_yield = pipeline.predict(features_df)[0]

        
        top_features = get_shap_explanation(features_df)

        predicted_revenue = 0
        crop_info = CROP_DATA.get(crop_input.capitalize())
        if crop_info:
            msp = crop_info['msp_per_quintal']
            predicted_revenue = (predicted_yield / 100) * msp
        
        recommendations = get_recommendations(district_input, year, area, weather_data, crop_input)

        return jsonify({
            "district": district_input.capitalize(),
            "crop": crop_input.capitalize(),
            "year": year,
            "area": area,
            "predicted_yield": round(float(predicted_yield), 2),
            "predicted_revenue": round(float(predicted_revenue), 2), 
            "weather": weather_data,
            "recommendations": recommendations,
            "explanations": top_features
        })
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
