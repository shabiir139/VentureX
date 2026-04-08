from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

companies = {}

# ==============================
# 🔹 SIMULATION ENGINE
# ==============================
def simulate_company(company):
    revenue = random.randint(10000, 50000)
    cost = random.randint(5000, 30000)
    profit = revenue - cost

    company["metrics"] = {
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "customer_satisfaction": random.randint(60, 95)
    }

    return company

# ==============================
# 🔹 LLM EXTENSIONS
# ==============================

def ai_mentor(company):
    prompt = f"""
    You are a business mentor.

    Analyze:
    Revenue: {company['metrics']['revenue']}
    Cost: {company['metrics']['cost']}
    Profit: {company['metrics']['profit']}
    Customer Satisfaction: {company['metrics']['customer_satisfaction']}

    Give advice, improvements, and strategy.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Expert startup mentor"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250
    )

    return response.choices[0].message.content


def investor_ai(company):
    prompt = f"""
    You are an investor.

    Company metrics:
    Profit: {company['metrics']['profit']}
    Revenue: {company['metrics']['revenue']}

    Decide:
    - Invest or not
    - Funding amount
    - Reason
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content


def scenario_ai():
    prompt = "Generate a real-world business disruption scenario."
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message.content


# ==============================
# 🔹 API ROUTES
# ==============================

@app.route("/")
def home():
    return "VentureX Backend Running with LLM Extensions"

@app.route("/create", methods=["POST"])
def create_company():
    data = request.json
    cid = str(len(companies) + 1)

    companies[cid] = {
        "id": cid,
        "name": data.get("name"),
        "metrics": {}
    }

    return jsonify(companies[cid])


@app.route("/simulate/<cid>", methods=["POST"])
def simulate(cid):
    company = companies.get(cid)

    if not company:
        return jsonify({"error": "Not found"}), 404

    company = simulate_company(company)

    mentor = ai_mentor(company)
    investor = investor_ai(company)
    scenario = scenario_ai()

    return jsonify({
        "company": company,
        "ai_mentor": mentor,
        "investor_ai": investor,
        "scenario": scenario
    })


if __name__ == "__main__":
    app.run(debug=True)
