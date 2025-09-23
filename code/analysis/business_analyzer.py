#!/usr/bin/env python3
"""
Business Analysis Engine for Rental Property Data
Computes deterministic business metrics and KPIs from rental property data.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from pathlib import Path


class RentalPropertyAnalyzer:
    """
    Comprehensive business analysis engine for rental property data.
    Computes deterministic metrics for portfolio optimization and business intelligence.
    """
    
    def __init__(self, data_path: str = "code/sample-data/rental-statements/labels.csv"):
        """Initialize analyzer with data path."""
        self.data_path = data_path
        self.df = None
        self.results = {}
        
    def load_data(self) -> pd.DataFrame:
        """Load and preprocess rental statement data."""
        try:
            # Load the CSV file, skipping the first row which contains column headers
            self.df = pd.read_csv(self.data_path, skiprows=1)
            
            # Convert date columns to datetime
            date_columns = ['statement_date', 'period_start', 'period_end', 'pay_date']
            for col in date_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['rent', 'management_fee', 'repair', 'deposit', 'misc', 'total']
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            print(f"Loaded {len(self.df)} records from {self.data_path}")
            return self.df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def compute_property_kpis(self) -> Dict[str, Any]:
        """Compute property-level Key Performance Indicators."""
        if self.df is None:
            return {}
        
        kpis = {}
        
        # Group by property
        property_groups = self.df.groupby('property_alias')
        
        for property_name, group in property_groups:
            property_kpis = {}
            
            # Basic financial metrics
            total_rent = group['rent'].sum()
            total_mgmt_fee = group['management_fee'].sum()
            total_repair = group['repair'].sum()
            total_misc = group['misc'].sum()
            total_deposit = group['deposit'].sum()
            
            # Revenue metrics
            property_kpis['total_rental_income'] = float(total_rent)
            property_kpis['average_monthly_rent'] = float(group['rent'].mean())
            property_kpis['rent_volatility'] = float(group['rent'].std())
            
            # Cost metrics
            property_kpis['total_management_fees'] = float(total_mgmt_fee)
            property_kpis['total_repair_costs'] = float(total_repair)
            property_kpis['total_miscellaneous_costs'] = float(total_misc)
            property_kpis['total_deposits'] = float(total_deposit)
            
            # Efficiency ratios
            if total_rent > 0:
                property_kpis['management_fee_ratio'] = float((total_mgmt_fee / total_rent) * 100)
                property_kpis['repair_cost_ratio'] = float((total_repair / total_rent) * 100)
                property_kpis['misc_cost_ratio'] = float((total_misc / total_rent) * 100)
                property_kpis['total_cost_ratio'] = float(((total_mgmt_fee + total_repair + total_misc) / total_rent) * 100)
                property_kpis['net_yield'] = float(((total_rent - total_mgmt_fee - total_repair - total_misc) / total_rent) * 100)
            
            # Cash flow metrics
            property_kpis['net_cash_flow'] = float(total_rent - total_mgmt_fee - total_repair - total_misc)
            property_kpis['average_monthly_cash_flow'] = float(property_kpis['net_cash_flow'] / len(group))
            
            # Time-based metrics
            property_kpis['statement_count'] = len(group)
            property_kpis['date_range_months'] = (group['statement_date'].max() - group['statement_date'].min()).days / 30.44
            
            # Vacancy analysis
            zero_rent_count = (group['rent'] == 0).sum()
            property_kpis['vacancy_rate'] = float((zero_rent_count / len(group)) * 100)
            
            kpis[property_name] = property_kpis
        
        return kpis
    
    def compute_portfolio_metrics(self) -> Dict[str, Any]:
        """Compute portfolio-level metrics."""
        if self.df is None:
            return {}
        
        portfolio = {}
        
        # Overall portfolio metrics
        portfolio['total_properties'] = self.df['property_alias'].nunique()
        portfolio['total_statements'] = len(self.df)
        portfolio['total_rental_income'] = float(self.df['rent'].sum())
        portfolio['total_management_fees'] = float(self.df['management_fee'].sum())
        portfolio['total_repair_costs'] = float(self.df['repair'].sum())
        portfolio['total_miscellaneous_costs'] = float(self.df['misc'].sum())
        portfolio['total_deposits'] = float(self.df['deposit'].sum())
        
        # Portfolio efficiency
        total_costs = portfolio['total_management_fees'] + portfolio['total_repair_costs'] + portfolio['total_miscellaneous_costs']
        portfolio['total_costs'] = float(total_costs)
        portfolio['net_portfolio_value'] = float(portfolio['total_rental_income'] - total_costs)
        
        if portfolio['total_rental_income'] > 0:
            portfolio['portfolio_management_fee_ratio'] = float((portfolio['total_management_fees'] / portfolio['total_rental_income']) * 100)
            portfolio['portfolio_repair_cost_ratio'] = float((portfolio['total_repair_costs'] / portfolio['total_rental_income']) * 100)
            portfolio['portfolio_total_cost_ratio'] = float((total_costs / portfolio['total_rental_income']) * 100)
            portfolio['portfolio_net_yield'] = float((portfolio['net_portfolio_value'] / portfolio['total_rental_income']) * 100)
        
        # Time analysis
        portfolio['date_range_start'] = self.df['statement_date'].min().strftime('%Y-%m-%d')
        portfolio['date_range_end'] = self.df['statement_date'].max().strftime('%Y-%m-%d')
        portfolio['analysis_period_months'] = (self.df['statement_date'].max() - self.df['statement_date'].min()).days / 30.44
        
        # Monthly averages
        portfolio['average_monthly_rent'] = float(portfolio['total_rental_income'] / portfolio['analysis_period_months'])
        portfolio['average_monthly_costs'] = float(total_costs / portfolio['analysis_period_months'])
        portfolio['average_monthly_cash_flow'] = float(portfolio['net_portfolio_value'] / portfolio['analysis_period_months'])
        
        return portfolio
    
    def compute_seasonal_analysis(self) -> Dict[str, Any]:
        """Analyze seasonal patterns in rental income and costs."""
        if self.df is None:
            return {}
        
        seasonal = {}
        
        # Add month column
        self.df['month'] = self.df['statement_date'].dt.month
        
        # Monthly averages
        monthly_stats = self.df.groupby('month').agg({
            'rent': ['mean', 'sum', 'count'],
            'management_fee': ['mean', 'sum'],
            'repair': ['mean', 'sum'],
            'misc': ['mean', 'sum']
        }).round(2)
        
        seasonal['monthly_averages'] = {}
        for month in range(1, 13):
            month_name = datetime(2023, month, 1).strftime('%B')
            if month in monthly_stats.index:
                seasonal['monthly_averages'][month_name] = {
                    'average_rent': float(monthly_stats.loc[month, ('rent', 'mean')]),
                    'total_rent': float(monthly_stats.loc[month, ('rent', 'sum')]),
                    'statement_count': int(monthly_stats.loc[month, ('rent', 'count')]),
                    'average_management_fee': float(monthly_stats.loc[month, ('management_fee', 'mean')]),
                    'average_repair_cost': float(monthly_stats.loc[month, ('repair', 'mean')]),
                    'average_misc_cost': float(monthly_stats.loc[month, ('misc', 'mean')])
                }
            else:
                seasonal['monthly_averages'][month_name] = {
                    'average_rent': 0.0,
                    'total_rent': 0.0,
                    'statement_count': 0,
                    'average_management_fee': 0.0,
                    'average_repair_cost': 0.0,
                    'average_misc_cost': 0.0
                }
        
        # Seasonal trends
        rent_by_month = [seasonal['monthly_averages'][month]['average_rent'] for month in seasonal['monthly_averages']]
        seasonal['peak_rent_month'] = rent_by_month.index(max(rent_by_month)) + 1
        seasonal['lowest_rent_month'] = rent_by_month.index(min(rent_by_month)) + 1
        seasonal['rent_seasonality'] = float((max(rent_by_month) - min(rent_by_month)) / np.mean(rent_by_month) * 100)
        
        return seasonal
    
    def compute_cost_optimization_opportunities(self) -> Dict[str, Any]:
        """Identify cost optimization opportunities."""
        if self.df is None:
            return {}
        
        optimization = {}
        
        # Management fee analysis
        mgmt_fee_by_property = self.df.groupby('property_alias')['management_fee'].agg(['mean', 'sum'])
        rent_by_property = self.df.groupby('property_alias')['rent'].agg(['mean', 'sum'])
        
        optimization['management_fee_analysis'] = {}
        for property_name in mgmt_fee_by_property.index:
            avg_mgmt_fee = mgmt_fee_by_property.loc[property_name, 'mean']
            avg_rent = rent_by_property.loc[property_name, 'mean']
            mgmt_fee_ratio = (avg_mgmt_fee / avg_rent * 100) if avg_rent > 0 else 0
            
            optimization['management_fee_analysis'][property_name] = {
                'average_management_fee': float(avg_mgmt_fee),
                'average_rent': float(avg_rent),
                'management_fee_ratio': float(mgmt_fee_ratio),
                'industry_benchmark': 10.0,  # Industry standard
                'optimization_potential': float(max(0, mgmt_fee_ratio - 10.0)),
                'potential_annual_savings': float(max(0, (mgmt_fee_ratio - 10.0) / 100 * avg_rent * 12))
            }
        
        # Repair cost analysis
        repair_by_property = self.df.groupby('property_alias')['repair'].agg(['mean', 'sum', 'std'])
        optimization['repair_cost_analysis'] = {}
        
        for property_name in repair_by_property.index:
            avg_repair = repair_by_property.loc[property_name, 'mean']
            repair_volatility = repair_by_property.loc[property_name, 'std']
            
            optimization['repair_cost_analysis'][property_name] = {
                'average_repair_cost': float(avg_repair),
                'repair_cost_volatility': float(repair_volatility),
                'industry_benchmark': 15.0,  # Industry standard percentage
                'maintenance_efficiency_score': float(max(0, 100 - (avg_repair / rent_by_property.loc[property_name, 'mean'] * 100)))
            }
        
        # Overall optimization summary
        total_potential_savings = sum([opt['potential_annual_savings'] for opt in optimization['management_fee_analysis'].values()])
        optimization['total_optimization_potential'] = {
            'annual_savings_potential': float(total_potential_savings),
            'percentage_of_income': float((total_potential_savings / self.df['rent'].sum()) * 100),
            'roi_timeline_months': float(12)  # Assuming immediate implementation
        }
        
        return optimization
    
    def compute_risk_metrics(self) -> Dict[str, Any]:
        """Compute risk assessment metrics."""
        if self.df is None:
            return {}
        
        risk = {}
        
        # Payment risk analysis
        risk['payment_risk'] = {
            'zero_rent_statements': int((self.df['rent'] == 0).sum()),
            'zero_rent_percentage': float((self.df['rent'] == 0).sum() / len(self.df) * 100),
            'low_rent_statements': int((self.df['rent'] < self.df['rent'].quantile(0.25)).sum()),
            'payment_consistency_score': float(100 - ((self.df['rent'] == 0).sum() / len(self.df) * 100))
        }
        
        # Cost volatility analysis
        risk['cost_volatility'] = {
            'management_fee_volatility': float(self.df['management_fee'].std()),
            'repair_cost_volatility': float(self.df['repair'].std()),
            'total_cost_volatility': float((self.df['management_fee'] + self.df['repair'] + self.df['misc']).std()),
            'cash_flow_volatility': float((self.df['rent'] - self.df['management_fee'] - self.df['repair'] - self.df['misc']).std())
        }
        
        # Concentration risk
        property_concentration = self.df['property_alias'].value_counts(normalize=True)
        risk['concentration_risk'] = {
            'largest_property_share': float(property_concentration.iloc[0] * 100),
            'top_2_properties_share': float(property_concentration.iloc[:2].sum() * 100),
            'concentration_risk_score': float(property_concentration.iloc[0] * 100)  # Higher = more concentrated
        }
        
        # Overall risk score
        risk['overall_risk_score'] = float(
            (risk['payment_risk']['zero_rent_percentage'] * 0.4) +
            (risk['cost_volatility']['cash_flow_volatility'] / 100 * 0.3) +
            (risk['concentration_risk']['concentration_risk_score'] * 0.3)
        )
        
        return risk
    
    def compute_predictive_metrics(self) -> Dict[str, Any]:
        """Compute predictive analytics metrics."""
        if self.df is None:
            return {}
        
        predictive = {}
        
        # Trend analysis
        self.df_sorted = self.df.sort_values('statement_date')
        
        # Rent trend
        if len(self.df_sorted) > 1:
            rent_trend = np.polyfit(range(len(self.df_sorted)), self.df_sorted['rent'], 1)[0]
            predictive['rent_trend'] = {
                'monthly_change': float(rent_trend),
                'annual_projection': float(rent_trend * 12),
                'trend_direction': 'increasing' if rent_trend > 0 else 'decreasing'
            }
        
        # Cost trend
        total_costs = self.df_sorted['management_fee'] + self.df_sorted['repair'] + self.df_sorted['misc']
        if len(self.df_sorted) > 1:
            cost_trend = np.polyfit(range(len(self.df_sorted)), total_costs, 1)[0]
            predictive['cost_trend'] = {
                'monthly_change': float(cost_trend),
                'annual_projection': float(cost_trend * 12),
                'trend_direction': 'increasing' if cost_trend > 0 else 'decreasing'
            }
        
        # Cash flow trend
        cash_flow = self.df_sorted['rent'] - total_costs
        if len(self.df_sorted) > 1:
            cash_flow_trend = np.polyfit(range(len(self.df_sorted)), cash_flow, 1)[0]
            predictive['cash_flow_trend'] = {
                'monthly_change': float(cash_flow_trend),
                'annual_projection': float(cash_flow_trend * 12),
                'trend_direction': 'improving' if cash_flow_trend > 0 else 'declining'
            }
        
        # Forecasting
        last_month_rent = self.df_sorted['rent'].iloc[-1]
        last_month_costs = total_costs.iloc[-1]
        
        predictive['forecasts'] = {
            'next_month_rent_forecast': float(last_month_rent + predictive.get('rent_trend', {}).get('monthly_change', 0)),
            'next_month_costs_forecast': float(last_month_costs + predictive.get('cost_trend', {}).get('monthly_change', 0)),
            'next_month_cash_flow_forecast': float((last_month_rent + predictive.get('rent_trend', {}).get('monthly_change', 0)) - 
                                                   (last_month_costs + predictive.get('cost_trend', {}).get('monthly_change', 0)))
        }
        
        return predictive
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete business analysis and return all metrics."""
        print("Starting comprehensive business analysis...")
        
        # Load data
        if self.load_data() is None:
            return {}
        
        # Compute all metrics
        self.results = {
            'analysis_metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_source': self.data_path,
                'total_records': len(self.df),
                'analysis_version': '1.0'
            },
            'property_kpis': self.compute_property_kpis(),
            'portfolio_metrics': self.compute_portfolio_metrics(),
            'seasonal_analysis': self.compute_seasonal_analysis(),
            'cost_optimization': self.compute_cost_optimization_opportunities(),
            'risk_metrics': self.compute_risk_metrics(),
            'predictive_metrics': self.compute_predictive_metrics()
        }
        
        print("Analysis complete!")
        return self.results
    
    def save_results(self, output_path: str = "analysis/business_analysis_results.json"):
        """Save analysis results to JSON file."""
        if not self.results:
            print("No results to save. Run analysis first.")
            return
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to {output_path}")
    
    def print_summary(self):
        """Print a summary of key findings."""
        if not self.results:
            print("No results available. Run analysis first.")
            return
        
        portfolio = self.results['portfolio_metrics']
        optimization = self.results['cost_optimization']
        
        print("\n" + "="*60)
        print("BUSINESS ANALYSIS SUMMARY")
        print("="*60)
        print(f"Portfolio Value: £{portfolio['total_rental_income']:,.2f}")
        print(f"Net Cash Flow: £{portfolio['net_portfolio_value']:,.2f}")
        print(f"Portfolio Yield: {portfolio['portfolio_net_yield']:.1f}%")
        print(f"Management Fee Ratio: {portfolio['portfolio_management_fee_ratio']:.1f}%")
        print(f"Optimization Potential: £{optimization['total_optimization_potential']['annual_savings_potential']:,.2f}")
        print("="*60)


def main():
    """Main function to run the analysis."""
    analyzer = RentalPropertyAnalyzer()
    results = analyzer.run_complete_analysis()
    
    if results:
        analyzer.save_results()
        analyzer.print_summary()
        return results
    else:
        print("Analysis failed. Check data file.")
        return None


if __name__ == "__main__":
    main()
