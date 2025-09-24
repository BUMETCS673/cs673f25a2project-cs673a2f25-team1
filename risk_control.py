class RiskControl:
    def __init__(self, parsed_data):
        self.data = parsed_data

    def check_unusual_rent(self):
        rents = self.data.get("rent_history", [])
        if len(rents) >= 2:
            last, current = rents[-2], rents[-1]
            if (current - last) / last > 0.2:
                return {"risk": "High Rent Increase", "details": f"涨幅 {current-last}"}
        return None

    def check_invalid_dates(self):
        start = self.data.get("lease_start")
        end = self.data.get("lease_end")
        if start and end and end < start:
            return {"risk": "Invalid Lease Dates", "details": f"{start} - {end}"}
        return None

    def run_all_checks(self):
        results = []
        for check in [self.check_unusual_rent, self.check_invalid_dates]:
            res = check()
            if res:
                results.append(res)
        return results

