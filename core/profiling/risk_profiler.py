class RiskProfiler:
    RISK_PROFILES = [  # noqa: RUF012
        {"max_score": 8, "category": "conservative", "risk_aversion_coefficient": 4},
        {"max_score": 13, "category": "moderate", "risk_aversion_coefficient": 2.5},
        {"max_score": 17, "category": "risk_tolerant", "risk_aversion_coefficient": 1.5},
        {"max_score": 20, "category": "aggressive", "risk_aversion_coefficient": 0.8},
    ]
    
    def calculate_profile(self, answers):
        total_score = sum(answers)
        
        for profile in self.RISK_PROFILES:
            if total_score <= profile["max_score"]:
                return {
                    "total_score": total_score,
                    "category": profile["category"],
                    "risk_aversion_coefficient": profile["risk_aversion_coefficient"],
                }
        raise ValueError(f"No matching risk profile for score {total_score}")
