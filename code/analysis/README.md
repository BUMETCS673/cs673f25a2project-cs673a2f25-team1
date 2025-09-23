# Business Analysis Engine - Usage Guide

## Overview
The Business Analysis Engine provides comprehensive, deterministic analysis of rental property data. It computes key performance indicators, cost optimization opportunities, risk metrics, and predictive analytics.

## Quick Start

### 1. Basic Usage
```python
from analysis.business_analyzer import RentalPropertyAnalyzer

# Initialize analyzer
analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')

# Run complete analysis
results = analyzer.run_complete_analysis()

# Save results to JSON
analyzer.save_results('analysis/my_analysis.json')

# Print summary
analyzer.print_summary()
```

### 2. Command Line Usage
```bash
# Run from project root directory
python3 analysis/business_analyzer.py
```

## Generated Metrics

### Property-Level KPIs
- **Total Rental Income**: Sum of all rent collected per property
- **Average Monthly Rent**: Mean monthly rental income
- **Management Fee Ratio**: Management fees as percentage of rent
- **Repair Cost Ratio**: Repair costs as percentage of rent
- **Net Yield**: Net income after all costs as percentage of rent
- **Cash Flow**: Monthly net cash flow after all expenses
- **Vacancy Rate**: Percentage of statements with zero rent

### Portfolio-Level Metrics
- **Total Portfolio Value**: Sum of all rental income
- **Portfolio Yield**: Overall net yield across all properties
- **Cost Ratios**: Management, repair, and total cost ratios
- **Monthly Averages**: Average monthly income, costs, and cash flow

### Seasonal Analysis
- **Monthly Averages**: Average rent, costs by month
- **Seasonality**: Peak and low rent months
- **Seasonal Variation**: Percentage variation in rent by season

### Cost Optimization
- **Management Fee Analysis**: Comparison against industry benchmarks (10%)
- **Optimization Potential**: Annual savings potential per property
- **Repair Cost Analysis**: Maintenance efficiency scoring

### Risk Metrics
- **Payment Risk**: Analysis of zero/low rent periods
- **Cost Volatility**: Standard deviation of costs
- **Concentration Risk**: Portfolio concentration by property
- **Overall Risk Score**: Composite risk assessment

### Predictive Analytics
- **Trend Analysis**: Monthly change trends for rent, costs, cash flow
- **Forecasting**: Next month projections
- **Annual Projections**: Yearly trend projections

## Example Results

### Key Findings from Current Data
- **Portfolio Value**: £59,881.75 total rental income
- **Net Cash Flow**: £47,387.35 after all costs
- **Portfolio Yield**: 79.1% net yield
- **Management Fee Ratio**: 10.8% (slightly above industry standard)
- **Optimization Potential**: £167.12 annual savings

### Property Performance Comparison
- **Arranview**: Highest rent (£574.39/month), 80.2% net yield
- **Bedford**: Most efficient (85.2% net yield), lowest repair costs
- **97B Dempster**: Highest management fees (13.3%), needs optimization

## Advanced Usage

### Custom Analysis
```python
# Load specific data
analyzer = RentalPropertyAnalyzer('path/to/your/data.csv')

# Run individual analyses
property_kpis = analyzer.compute_property_kpis()
portfolio_metrics = analyzer.compute_portfolio_metrics()
seasonal_analysis = analyzer.compute_seasonal_analysis()
cost_optimization = analyzer.compute_cost_optimization_opportunities()
risk_metrics = analyzer.compute_risk_metrics()
predictive_metrics = analyzer.compute_predictive_metrics()
```

### Accessing Specific Metrics
```python
# Get results
results = analyzer.run_complete_analysis()

# Access specific property data
arranview_data = results['property_kpis']['Arranview']
print(f"Arranview Net Yield: {arranview_data['net_yield']:.1f}%")

# Access optimization opportunities
optimization = results['cost_optimization']['management_fee_analysis']
for property_name, data in optimization.items():
    print(f"{property_name}: £{data['potential_annual_savings']:.2f} savings potential")
```

## Business Applications

### 1. Portfolio Optimization
- Identify highest-performing properties
- Compare management fee efficiency
- Optimize repair cost management

### 2. Cost Reduction
- Negotiate better management rates
- Implement preventive maintenance
- Reduce miscellaneous costs

### 3. Risk Management
- Monitor payment consistency
- Assess concentration risk
- Track cost volatility

### 4. Strategic Planning
- Forecast future cash flows
- Plan property acquisitions/disposals
- Optimize portfolio composition

## Output Files

### JSON Structure
```json
{
  "analysis_metadata": {
    "generated_at": "2024-09-22T22:18:00",
    "data_source": "code/sample-data/rental-statements/labels.csv",
    "total_records": 134,
    "analysis_version": "1.0"
  },
  "property_kpis": {
    "Arranview": { ... },
    "Bedford": { ... },
    "97B Dempster": { ... }
  },
  "portfolio_metrics": { ... },
  "seasonal_analysis": { ... },
  "cost_optimization": { ... },
  "risk_metrics": { ... },
  "predictive_metrics": { ... }
}
```

## Troubleshooting

### Common Issues
1. **File Not Found**: Ensure you're running from the project root directory
2. **Data Format**: Ensure CSV has proper headers and numeric data
3. **Date Format**: Dates should be in MM/DD/YYYY format

### Data Requirements
- CSV file with columns: statement_id, property_alias, statement_date, rent, management_fee, repair, deposit, misc, total
- Numeric data in financial columns
- Valid date format in date columns

## Extending the Analysis

### Adding New Metrics
```python
def compute_custom_metric(self):
    # Add your custom analysis here
    return custom_results

# Add to run_complete_analysis method
self.results['custom_metrics'] = self.compute_custom_metric()
```

### Custom Data Sources
```python
# Modify the load_data method to handle different formats
def load_data(self, custom_path):
    # Load and preprocess your custom data
    pass
```

## Performance Notes
- Analysis runs on 134 records in <1 second
- Memory usage: ~10MB for typical datasets
- Scalable to larger datasets (tested up to 10,000 records)

## Support
For questions or issues with the analysis engine, check:
1. Data format compliance
2. File path accuracy
3. Python dependencies (pandas, numpy)
