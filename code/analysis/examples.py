#!/usr/bin/env python3
"""
Example usage scripts for the Business Analysis Engine
Demonstrates how to use the analysis functions for different business scenarios.
"""

import json
import sys
import os

# Ensure local imports work regardless of CWD
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from business_analyzer import RentalPropertyAnalyzer


def example_basic_analysis():
    """Example 1: Basic analysis and summary."""
    print("="*60)
    print("EXAMPLE 1: Basic Analysis")
    print("="*60)
    
    analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')
    results = analyzer.run_complete_analysis()
    
    if results:
        analyzer.print_summary()
        print("\n✓ Analysis complete! Results saved next to this script (business_analysis_results.json)")
    else:
        print("✗ Analysis failed")


def example_property_comparison():
    """Example 2: Compare property performance."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Property Performance Comparison")
    print("="*60)
    
    analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')
    analyzer.load_data()
    
    property_kpis = analyzer.compute_property_kpis()
    
    print("Property Performance Ranking:")
    print("-" * 40)
    
    # Sort by net yield
    sorted_properties = sorted(
        property_kpis.items(), 
        key=lambda x: x[1]['net_yield'], 
        reverse=True
    )
    
    for i, (property_name, data) in enumerate(sorted_properties, 1):
        print(f"{i}. {property_name}")
        print(f"   Net Yield: {data['net_yield']:.1f}%")
        print(f"   Avg Monthly Rent: £{data['average_monthly_rent']:.2f}")
        print(f"   Management Fee Ratio: {data['management_fee_ratio']:.1f}%")
        print(f"   Monthly Cash Flow: £{data['average_monthly_cash_flow']:.2f}")
        print()


def example_cost_optimization():
    """Example 3: Identify cost optimization opportunities."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Cost Optimization Opportunities")
    print("="*60)
    
    analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')
    analyzer.load_data()
    
    optimization = analyzer.compute_cost_optimization_opportunities()
    
    print("Management Fee Optimization:")
    print("-" * 30)
    
    mgmt_analysis = optimization['management_fee_analysis']
    for property_name, data in mgmt_analysis.items():
        if data['optimization_potential'] > 0:
            print(f"{property_name}:")
            print(f"  Current Fee Ratio: {data['management_fee_ratio']:.1f}%")
            print(f"  Industry Benchmark: {data['industry_benchmark']:.1f}%")
            print(f"  Optimization Potential: {data['optimization_potential']:.1f}%")
            print(f"  Annual Savings: £{data['potential_annual_savings']:.2f}")
            print()
    
    total_savings = optimization['total_optimization_potential']['annual_savings_potential']
    print(f"Total Annual Savings Potential: £{total_savings:.2f}")


def example_risk_assessment():
    """Example 4: Risk assessment analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Risk Assessment")
    print("="*60)
    
    analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')
    analyzer.load_data()
    
    risk = analyzer.compute_risk_metrics()
    
    print("Portfolio Risk Analysis:")
    print("-" * 25)
    print(f"Payment Risk Score: {risk['payment_risk']['payment_consistency_score']:.1f}/100")
    print(f"Zero Rent Statements: {risk['payment_risk']['zero_rent_statements']}")
    print(f"Vacancy Rate: {risk['payment_risk']['zero_rent_percentage']:.1f}%")
    print()
    
    print("Cost Volatility:")
    print(f"Management Fee Volatility: £{risk['cost_volatility']['management_fee_volatility']:.2f}")
    print(f"Repair Cost Volatility: £{risk['cost_volatility']['repair_cost_volatility']:.2f}")
    print(f"Cash Flow Volatility: £{risk['cost_volatility']['cash_flow_volatility']:.2f}")
    print()
    
    print("Concentration Risk:")
    print(f"Largest Property Share: {risk['concentration_risk']['largest_property_share']:.1f}%")
    print(f"Top 2 Properties Share: {risk['concentration_risk']['top_2_properties_share']:.1f}%")
    print()
    
    print(f"Overall Risk Score: {risk['overall_risk_score']:.1f}/100")


def example_predictive_analytics():
    """Example 5: Predictive analytics and forecasting."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Predictive Analytics")
    print("="*60)
    
    analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')
    analyzer.load_data()
    
    predictive = analyzer.compute_predictive_metrics()
    
    print("Trend Analysis:")
    print("-" * 15)
    
    if 'rent_trend' in predictive:
        rent_trend = predictive['rent_trend']
        print(f"Rent Trend: {rent_trend['trend_direction']}")
        print(f"Monthly Change: £{rent_trend['monthly_change']:.2f}")
        print(f"Annual Projection: £{rent_trend['annual_projection']:.2f}")
        print()
    
    if 'cost_trend' in predictive:
        cost_trend = predictive['cost_trend']
        print(f"Cost Trend: {cost_trend['trend_direction']}")
        print(f"Monthly Change: £{cost_trend['monthly_change']:.2f}")
        print(f"Annual Projection: £{cost_trend['annual_projection']:.2f}")
        print()
    
    if 'cash_flow_trend' in predictive:
        cash_flow_trend = predictive['cash_flow_trend']
        print(f"Cash Flow Trend: {cash_flow_trend['trend_direction']}")
        print(f"Monthly Change: £{cash_flow_trend['monthly_change']:.2f}")
        print(f"Annual Projection: £{cash_flow_trend['annual_projection']:.2f}")
        print()
    
    print("Next Month Forecasts:")
    print("-" * 20)
    forecasts = predictive['forecasts']
    print(f"Rent Forecast: £{forecasts['next_month_rent_forecast']:.2f}")
    print(f"Costs Forecast: £{forecasts['next_month_costs_forecast']:.2f}")
    print(f"Cash Flow Forecast: £{forecasts['next_month_cash_flow_forecast']:.2f}")


def example_seasonal_analysis():
    """Example 6: Seasonal analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Seasonal Analysis")
    print("="*60)
    
    analyzer = RentalPropertyAnalyzer('code/sample-data/rental-statements/labels.csv')
    analyzer.load_data()
    
    seasonal = analyzer.compute_seasonal_analysis()
    
    print("Seasonal Patterns:")
    print("-" * 18)
    print(f"Peak Rent Month: {seasonal['peak_rent_month']}")
    print(f"Lowest Rent Month: {seasonal['lowest_rent_month']}")
    print(f"Rent Seasonality: {seasonal['rent_seasonality']:.1f}%")
    print()
    
    print("Monthly Rent Averages:")
    print("-" * 22)
    monthly_avg = seasonal['monthly_averages']
    for month, data in monthly_avg.items():
        if data['statement_count'] > 0:
            print(f"{month}: £{data['average_rent']:.2f} ({data['statement_count']} statements)")


def example_custom_analysis():
    """Example 7: Custom analysis using JSON results."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Custom Analysis from JSON")
    print("="*60)
    
    # Load existing results
    try:
        with open(os.path.join(CURRENT_DIR, 'business_analysis_results.json'), 'r') as f:
            results = json.load(f)
        
        print("Custom Analysis: Top Performing Properties")
        print("-" * 40)
        
        # Find properties with highest net yield
        property_kpis = results['property_kpis']
        sorted_properties = sorted(
            property_kpis.items(),
            key=lambda x: x[1]['net_yield'],
            reverse=True
        )
        
        print("Top 3 Properties by Net Yield:")
        for i, (property_name, data) in enumerate(sorted_properties[:3], 1):
            print(f"{i}. {property_name}: {data['net_yield']:.1f}% yield")
        
        print("\nCustom Analysis: Cost Efficiency")
        print("-" * 30)
        
        # Find most cost-efficient properties
        sorted_by_efficiency = sorted(
            property_kpis.items(),
            key=lambda x: x[1]['total_cost_ratio']
        )
        
        print("Most Cost-Efficient Properties:")
        for i, (property_name, data) in enumerate(sorted_by_efficiency[:3], 1):
            print(f"{i}. {property_name}: {data['total_cost_ratio']:.1f}% total costs")
        
    except FileNotFoundError:
        print("Results file not found. Run basic analysis first.")


def main():
    """Run all examples."""
    print("BUSINESS ANALYSIS ENGINE - USAGE EXAMPLES")
    print("=" * 60)
    
    # Run all examples
    example_basic_analysis()
    example_property_comparison()
    example_cost_optimization()
    example_risk_assessment()
    example_predictive_analytics()
    example_seasonal_analysis()
    example_custom_analysis()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED")
    print("="*60)
    print("\nTo run individual examples:")
    print("python3 analysis/examples.py")
    print("\nTo run the main analyzer:")
    print("python3 analysis/business_analyzer.py")


if __name__ == "__main__":
    main()
