"""
Data Science Agent - Specialized in Data Analysis and Machine Learning

This agent handles:
- Data exploration and analysis
- Statistical modeling and hypothesis testing
- Machine learning model development
- Data visualization and reporting
- Feature engineering and selection
- Model evaluation and deployment
"""

import re
import json
import statistics
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score

from .base_agent import BaseAgent


class DataScienceAgent(BaseAgent):
    """Specialized data science agent for analysis and machine learning tasks."""

    def __init__(self, name: str = "data_science_agent", **kwargs):
        super().__init__(
            name=name,
            description="Specialized in data analysis, statistical modeling, and machine learning",
            capabilities=[
                "data_exploration", "statistical_analysis", "machine_learning",
                "feature_engineering", "data_visualization", "model_evaluation",
                "predictive_modeling", "hypothesis_testing", "data_preprocessing"
            ],
            personality={
                "expertise_level": "expert",
                "communication_style": "analytical",
                "specialties": ["data_science", "statistics", "machine_learning"]
            },
            **kwargs
        )

        # Data science knowledge base
        self.ml_algorithms = self._get_ml_algorithms()
        self.statistical_tests = self._get_statistical_tests()
        self.data_patterns = self._get_data_patterns()
        self.visualization_templates = self._get_visualization_templates()

    def _get_ml_algorithms(self) -> Dict[str, Any]:
        """Get machine learning algorithms and their use cases."""
        return {
            "classification": {
                "algorithms": {
                    "random_forest": {
                        "description": "Ensemble method using multiple decision trees",
                        "use_case": "General classification with mixed data types",
                        "pros": ["Handles missing values", "Reduces overfitting", "Feature importance"],
                        "cons": ["Can be slow", "Less interpretable"],
                        "parameters": ["n_estimators", "max_depth", "min_samples_split"]
                    },
                    "logistic_regression": {
                        "description": "Linear model for binary/multiclass classification",
                        "use_case": "Binary classification with linear relationships",
                        "pros": ["Fast training", "Highly interpretable", "Probabilistic output"],
                        "cons": ["Assumes linear relationships", "Sensitive to outliers"],
                        "parameters": ["C", "penalty", "max_iter"]
                    },
                    "svm": {
                        "description": "Support Vector Machine for classification",
                        "use_case": "High-dimensional data with clear margins",
                        "pros": ["Effective in high dimensions", "Memory efficient"],
                        "cons": ["Slow training", "Requires parameter tuning"],
                        "parameters": ["C", "kernel", "gamma"]
                    }
                }
            },
            "regression": {
                "algorithms": {
                    "linear_regression": {
                        "description": "Linear approach to modeling relationship between variables",
                        "use_case": "Predicting continuous values with linear relationships",
                        "pros": ["Simple and interpretable", "Fast training"],
                        "cons": ["Assumes linear relationships", "Sensitive to outliers"],
                        "parameters": ["fit_intercept", "normalize"]
                    },
                    "random_forest": {
                        "description": "Ensemble of decision trees for regression",
                        "use_case": "Non-linear relationships with mixed data types",
                        "pros": ["Handles non-linear relationships", "Feature importance"],
                        "cons": ["Can overfit", "Less interpretable"],
                        "parameters": ["n_estimators", "max_depth", "min_samples_split"]
                    },
                    "gradient_boosting": {
                        "description": "Sequential ensemble method",
                        "use_case": "Complex non-linear relationships",
                        "pros": ["High accuracy", "Handles missing values"],
                        "cons": ["Slow training", "Prone to overfitting"],
                        "parameters": ["n_estimators", "learning_rate", "max_depth"]
                    }
                }
            },
            "clustering": {
                "algorithms": {
                    "kmeans": {
                        "description": "Partition data into k clusters",
                        "use_case": "Spherical clusters of similar size",
                        "pros": ["Simple and fast", "Scalable"],
                        "cons": ["Assumes spherical clusters", "Requires k specification"],
                        "parameters": ["n_clusters", "init", "n_init"]
                    },
                    "hierarchical": {
                        "description": "Build hierarchy of clusters",
                        "use_case": "Understanding data hierarchy",
                        "pros": ["No need to specify k", "Dendrogram visualization"],
                        "cons": ["Slow on large datasets", "Cannot undo merges"],
                        "parameters": ["n_clusters", "linkage", "affinity"]
                    }
                }
            }
        }

    def _get_statistical_tests(self) -> Dict[str, Any]:
        """Get statistical tests and their applications."""
        return {
            "normality_tests": {
                "shapiro_wilk": {
                    "description": "Test for normality in small samples",
                    "use_case": "Testing if data follows normal distribution",
                    "assumptions": "Continuous data, n < 5000",
                    "interpretation": "p > 0.05 indicates normality"
                },
                "kolmogorov_smirnov": {
                    "description": "Test for normality against known distribution",
                    "use_case": "Comparing sample to normal distribution",
                    "assumptions": "Continuous data",
                    "interpretation": "p > 0.05 indicates normality"
                }
            },
            "comparative_tests": {
                "t_test": {
                    "description": "Compare means of two groups",
                    "use_case": "Testing difference between two group means",
                    "types": ["one-sample", "two-sample", "paired"],
                    "assumptions": "Normality, equal variances, independence",
                    "interpretation": "p < 0.05 indicates significant difference"
                },
                "anova": {
                    "description": "Compare means across multiple groups",
                    "use_case": "Testing differences between three or more groups",
                    "assumptions": "Normality, equal variances, independence",
                    "interpretation": "p < 0.05 indicates at least one significant difference"
                },
                "chi_square": {
                    "description": "Test association between categorical variables",
                    "use_case": "Testing independence between categorical variables",
                    "assumptions": "Expected frequency >= 5 in 80% of cells",
                    "interpretation": "p < 0.05 indicates association exists"
                }
            },
            "correlation_tests": {
                "pearson": {
                    "description": "Linear correlation between continuous variables",
                    "use_case": "Measuring strength of linear relationship",
                    "assumptions": "Normality, linearity, homoscedasticity",
                    "interpretation": "|r| > 0.7 indicates strong correlation"
                },
                "spearman": {
                    "description": "Monotonic correlation between variables",
                    "use_case": "Measuring monotonic relationships",
                    "assumptions": "Ordinal or continuous data",
                    "interpretation": "|ρ| > 0.7 indicates strong correlation"
                }
            }
        }

    def _get_data_patterns(self) -> Dict[str, Any]:
        """Get data preprocessing and feature engineering patterns."""
        return {
            "preprocessing": {
                "handling_missing_values": {
                    "strategies": [
                        {"method": "drop", "description": "Remove rows/columns with missing values"},
                        {"method": "mean", "description": "Replace with mean (numerical)"},
                        {"method": "median", "description": "Replace with median (numerical)"},
                        {"method": "mode", "description": "Replace with mode (categorical)"},
                        {"method": "interpolate", "description": "Use interpolation methods"}
                    ]
                },
                "encoding_categorical": {
                    "strategies": [
                        {"method": "label_encoding", "description": "Ordinal categories (good, better, best)"},
                        {"method": "one_hot_encoding", "description": "Nominal categories without order"},
                        {"method": "target_encoding", "description": "Encode based on target variable mean"}
                    ]
                },
                "feature_scaling": {
                    "methods": [
                        {"method": "standardization", "description": "Zero mean, unit variance"},
                        {"method": "normalization", "description": "Scale to [0,1] range"},
                        {"method": "robust_scaling", "description": "Use median and IQR"}
                    ]
                }
            },
            "feature_engineering": {
                "techniques": [
                    {
                        "name": "binning",
                        "description": "Convert continuous to categorical",
                        "use_case": "Handle outliers, non-linear relationships"
                    },
                    {
                        "name": "polynomial_features",
                        "description": "Create polynomial combinations",
                        "use_case": "Capture non-linear relationships"
                    },
                    {
                        "name": "interaction_features",
                        "description": "Multiply features together",
                        "use_case": "Capture feature interactions"
                    },
                    {
                        "name": "datetime_features",
                        "description": "Extract year, month, day, hour from dates",
                        "use_case": "Time series and temporal patterns"
                    }
                ]
            }
        }

    def _get_visualization_templates(self) -> Dict[str, Any]:
        """Get data visualization templates."""
        return {
            "univariate": {
                "histogram": {
                    "description": "Distribution of single numerical variable",
                    "use_case": "Understanding data distribution and outliers",
                    "code": """
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='column_name', bins=30, kde=True)
plt.title('Distribution of Column Name')
plt.xlabel('Column Name')
plt.ylabel('Frequency')
plt.show()
"""
                },
                "boxplot": {
                    "description": "Box plot for distribution and outliers",
                    "use_case": "Identifying outliers and distribution shape",
                    "code": """
plt.figure(figsize=(8, 6))
sns.boxplot(data=df, y='column_name')
plt.title('Box Plot of Column Name')
plt.ylabel('Column Name')
plt.show()
"""
                }
            },
            "bivariate": {
                "scatterplot": {
                    "description": "Relationship between two numerical variables",
                    "use_case": "Understanding correlation and patterns",
                    "code": """
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='x_column', y='y_column', hue='category_column')
plt.title('Relationship between X and Y')
plt.xlabel('X Column')
plt.ylabel('Y Column')
plt.show()
"""
                },
                "correlation_heatmap": {
                    "description": "Correlation matrix visualization",
                    "use_case": "Understanding relationships between multiple variables",
                    "code": """
plt.figure(figsize=(12, 8))
correlation_matrix = df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Heatmap')
plt.show()
"""
                }
            },
            "multivariate": {
                "pairplot": {
                    "description": "Pairwise relationships in dataset",
                    "use_case": "Understanding multiple variable relationships",
                    "code": """
sns.pairplot(df, hue='target_column', diag_kind='kde')
plt.suptitle('Pairwise Relationships', y=1.02)
plt.show()
"""
                }
            }
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data science-related tasks."""
        task_type = task.get("type", "")
        operation = task.get("operation", "")

        if task_type == "data_analysis":
            return await self._handle_data_analysis(task)
        elif task_type == "machine_learning":
            return await self._handle_machine_learning(task)
        elif task_type == "statistical_testing":
            return await self._handle_statistical_testing(task)
        elif task_type == "data_visualization":
            return await self._handle_data_visualization(task)
        elif task_type == "feature_engineering":
            return await self._handle_feature_engineering(task)
        else:
            # Use general task execution for other data science tasks
            return await super().execute_task(task)

    async def _handle_data_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data analysis tasks."""
        operation = task.get("operation", "")

        if operation == "explore_dataset":
            return await self._explore_dataset(task)
        elif operation == "data_quality_check":
            return await self._check_data_quality(task)
        elif operation == "generate_summary":
            return await self._generate_data_summary(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown data analysis operation: {operation}"
            }

    async def _handle_machine_learning(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle machine learning tasks."""
        operation = task.get("operation", "")

        if operation == "train_model":
            return await self._train_ml_model(task)
        elif operation == "evaluate_model":
            return await self._evaluate_ml_model(task)
        elif operation == "hyperparameter_tuning":
            return await self._tune_hyperparameters(task)
        elif operation == "feature_importance":
            return await self._analyze_feature_importance(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown ML operation: {operation}"
            }

    async def _handle_statistical_testing(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle statistical testing tasks."""
        operation = task.get("operation", "")

        if operation == "hypothesis_test":
            return await self._perform_hypothesis_test(task)
        elif operation == "correlation_analysis":
            return await self._analyze_correlation(task)
        elif operation == "distribution_test":
            return await self._test_distribution(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown statistical operation: {operation}"
            }

    async def _handle_data_visualization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data visualization tasks."""
        operation = task.get("operation", "")

        if operation == "create_chart":
            return await self._create_visualization(task)
        elif operation == "generate_report":
            return await self._generate_visualization_report(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown visualization operation: {operation}"
            }

    async def _handle_feature_engineering(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle feature engineering tasks."""
        operation = task.get("operation", "")

        if operation == "create_features":
            return await self._create_features(task)
        elif operation == "select_features":
            return await self._select_features(task)
        elif operation == "encode_variables":
            return await self._encode_variables(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown feature engineering operation: {operation}"
            }

    async def _explore_dataset(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Explore and analyze a dataset."""
        # This is a simplified implementation - in real usage, you'd load actual data
        data_description = task.get("data_description", {})
        sample_data = task.get("sample_data", [])

        try:
            # Basic data exploration
            if sample_data:
                df_info = self._analyze_dataframe(sample_data)
            else:
                df_info = {"message": "No sample data provided"}

            # Generate insights
            insights = self._generate_data_insights(data_description, df_info)

            return {
                "status": "completed",
                "result": {
                    "data_info": df_info,
                    "insights": insights,
                    "recommendations": self._generate_data_recommendations(df_info)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Data exploration failed: {str(e)}"
            }

    def _analyze_dataframe(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze dataframe structure and statistics."""
        if not data:
            return {}

        df = pd.DataFrame(data)

        info = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated().sum()
        }

        # Numerical columns statistics
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            info["numerical_stats"] = df[numerical_cols].describe().to_dict()

        # Categorical columns statistics
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            info["categorical_stats"] = {}
            for col in categorical_cols:
                info["categorical_stats"][col] = {
                    "unique_values": df[col].nunique(),
                    "most_common": df[col].value_counts().head(5).to_dict()
                }

        return info

    def _generate_data_insights(self, description: Dict[str, Any], df_info: Dict[str, Any]) -> List[str]:
        """Generate insights from data analysis."""
        insights = []

        if "shape" in df_info:
            rows, cols = df_info["shape"]
            insights.append(f"Dataset contains {rows} rows and {cols} columns")

        if "missing_values" in df_info:
            missing_cols = [col for col, count in df_info["missing_values"].items() if count > 0]
            if missing_cols:
                insights.append(f"Found missing values in columns: {', '.join(missing_cols)}")

        if "duplicates" in df_info and df_info["duplicates"] > 0:
            insights.append(f"Dataset contains {df_info['duplicates']} duplicate rows")

        if "numerical_stats" in df_info:
            insights.append("Dataset contains numerical features suitable for regression/classification")

        if "categorical_stats" in df_info:
            insights.append("Dataset contains categorical features requiring encoding")

        return insights

    def _generate_data_recommendations(self, df_info: Dict[str, Any]) -> List[str]:
        """Generate data preprocessing recommendations."""
        recommendations = []

        if "missing_values" in df_info:
            missing_cols = [col for col, count in df_info["missing_values"].items() if count > 0]
            if missing_cols:
                recommendations.append("Handle missing values using imputation or removal strategies")

        if "duplicates" in df_info and df_info["duplicates"] > 0:
            recommendations.append("Remove duplicate rows to ensure data quality")

        if "categorical_stats" in df_info:
            recommendations.append("Encode categorical variables for machine learning models")

        if "numerical_stats" in df_info:
            recommendations.append("Consider feature scaling for distance-based algorithms")

        recommendations.append("Perform exploratory data analysis with visualizations")
        recommendations.append("Check for outliers and handle them appropriately")

        return recommendations

    async def _train_ml_model(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Train a machine learning model."""
        model_type = task.get("model_type", "classification")
        algorithm = task.get("algorithm", "random_forest")
        target_column = task.get("target_column", "")
        feature_columns = task.get("feature_columns", [])

        try:
            # This is a simplified implementation - in real usage, you'd load actual data
            # For demonstration, we'll create mock training

            # Mock training process
            model_info = {
                "model_type": model_type,
                "algorithm": algorithm,
                "target_column": target_column,
                "feature_columns": feature_columns,
                "training_samples": 1000,
                "features_used": len(feature_columns)
            }

            # Mock performance metrics
            if model_type == "classification":
                metrics = {
                    "accuracy": 0.85,
                    "precision": 0.83,
                    "recall": 0.87,
                    "f1_score": 0.85
                }
            else:  # regression
                metrics = {
                    "mse": 0.15,
                    "rmse": 0.387,
                    "mae": 0.28,
                    "r2_score": 0.82
                }

            # Mock feature importance
            feature_importance = {}
            for feature in feature_columns:
                feature_importance[feature] = round(np.random.uniform(0.01, 0.3), 3)

            return {
                "status": "completed",
                "result": {
                    "model_info": model_info,
                    "performance_metrics": metrics,
                    "feature_importance": feature_importance,
                    "training_time": "45.2 seconds",
                    "model_size": "2.3 MB"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Model training failed: {str(e)}"
            }

    async def _evaluate_ml_model(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a trained machine learning model."""
        model_type = task.get("model_type", "classification")
        evaluation_metrics = task.get("metrics", [])

        try:
            # Mock evaluation results
            evaluation_results = {}

            if model_type == "classification":
                evaluation_results = {
                    "accuracy": 0.82,
                    "precision": 0.79,
                    "recall": 0.85,
                    "f1_score": 0.82,
                    "auc_roc": 0.88,
                    "confusion_matrix": {
                        "true_positive": 45,
                        "true_negative": 38,
                        "false_positive": 12,
                        "false_negative": 8
                    }
                }
            else:  # regression
                evaluation_results = {
                    "mean_squared_error": 0.18,
                    "root_mean_squared_error": 0.424,
                    "mean_absolute_error": 0.31,
                    "r_squared": 0.79,
                    "explained_variance": 0.81
                }

            # Generate recommendations
            recommendations = self._generate_model_recommendations(evaluation_results, model_type)

            return {
                "status": "completed",
                "result": {
                    "evaluation_metrics": evaluation_results,
                    "recommendations": recommendations,
                    "model_performance": "good" if evaluation_results.get("accuracy", evaluation_results.get("r_squared", 0)) > 0.8 else "needs_improvement"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Model evaluation failed: {str(e)}"
            }

    def _generate_model_recommendations(self, metrics: Dict[str, Any], model_type: str) -> List[str]:
        """Generate model improvement recommendations."""
        recommendations = []

        if model_type == "classification":
            accuracy = metrics.get("accuracy", 0)
            if accuracy < 0.7:
                recommendations.append("Consider trying different algorithms or ensemble methods")
            if accuracy > 0.9:
                recommendations.append("Model shows excellent performance - consider deployment")

            precision = metrics.get("precision", 0)
            recall = metrics.get("recall", 0)
            if precision > recall:
                recommendations.append("Model favors precision over recall - adjust threshold if needed")
            elif recall > precision:
                recommendations.append("Model favors recall over precision - adjust threshold if needed")

        else:  # regression
            r2 = metrics.get("r_squared", 0)
            if r2 < 0.5:
                recommendations.append("Model explains limited variance - try more complex algorithms")
            if r2 > 0.8:
                recommendations.append("Model shows good explanatory power")

            mse = metrics.get("mean_squared_error", 0)
            if mse > 1.0:
                recommendations.append("Consider feature scaling or different preprocessing")

        recommendations.append("Perform cross-validation to ensure model stability")
        recommendations.append("Check for overfitting using learning curves")

        return recommendations

    async def _perform_hypothesis_test(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical hypothesis testing."""
        test_type = task.get("test_type", "t_test")
        data_description = task.get("data_description", {})

        try:
            # Mock statistical test results
            test_results = {}

            if test_type == "t_test":
                test_results = {
                    "test_statistic": 2.45,
                    "p_value": 0.014,
                    "degrees_of_freedom": 98,
                    "confidence_interval": [0.23, 1.45],
                    "effect_size": 0.35
                }
            elif test_type == "anova":
                test_results = {
                    "f_statistic": 3.67,
                    "p_value": 0.028,
                    "degrees_of_freedom": [2, 147],
                    "effect_size": 0.29
                }
            elif test_type == "chi_square":
                test_results = {
                    "chi_square_statistic": 12.45,
                    "p_value": 0.006,
                    "degrees_of_freedom": 3,
                    "cramers_v": 0.22
                }

            # Generate interpretation
            interpretation = self._interpret_statistical_test(test_results, test_type)

            return {
                "status": "completed",
                "result": {
                    "test_type": test_type,
                    "test_results": test_results,
                    "interpretation": interpretation,
                    "significance_level": 0.05
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Statistical test failed: {str(e)}"
            }

    def _interpret_statistical_test(self, results: Dict[str, Any], test_type: str) -> str:
        """Interpret statistical test results."""
        p_value = results.get("p_value", 1.0)

        if p_value < 0.05:
            significance = "statistically significant"
            conclusion = "reject the null hypothesis"
        else:
            significance = "not statistically significant"
            conclusion = "fail to reject the null hypothesis"

        if test_type == "t_test":
            return f"The difference between groups is {significance} (p = {p_value:.3f}). We {conclusion}."
        elif test_type == "anova":
            return f"There are {significance} differences between groups (p = {p_value:.3f}). We {conclusion}."
        elif test_type == "chi_square":
            return f"There is {significance} association between variables (p = {p_value:.3f}). We {conclusion}."
        else:
            return f"Results are {significance} (p = {p_value:.3f})."

    async def _create_visualization(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create data visualizations."""
        chart_type = task.get("chart_type", "scatterplot")
        data_description = task.get("data_description", {})

        try:
            # Get visualization template
            template = self.visualization_templates.get("bivariate", {}).get(chart_type, {})

            if not template:
                return {
                    "status": "error",
                    "message": f"Visualization type '{chart_type}' not supported"
                }

            # Customize template with data description
            code = template.get("code", "")
            variables = task.get("variables", {})

            for key, value in variables.items():
                code = code.replace(f"{{{key}}}", str(value))

            return {
                "status": "completed",
                "result": {
                    "chart_type": chart_type,
                    "visualization_code": code,
                    "description": template.get("description", ""),
                    "libraries": ["matplotlib", "seaborn", "pandas"],
                    "filename": f"{chart_type}_visualization.py"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Visualization creation failed: {str(e)}"
            }

    async def _create_features(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create new features from existing data."""
        feature_type = task.get("feature_type", "polynomial")
        base_features = task.get("base_features", [])

        try:
            new_features = []
            feature_code = []

            if feature_type == "polynomial":
                for feature in base_features:
                    new_features.extend([
                        f"{feature}_squared",
                        f"{feature}_cubed",
                        f"sqrt_{feature}"
                    ])
                    feature_code.append(f"df['{feature}_squared'] = df['{feature}'] ** 2")
                    feature_code.append(f"df['{feature}_cubed'] = df['{feature}'] ** 3")
                    feature_code.append(f"df['{feature}_sqrt'] = np.sqrt(df['{feature}'])")

            elif feature_type == "interaction":
                for i, feature1 in enumerate(base_features):
                    for feature2 in base_features[i+1:]:
                        interaction_name = f"{feature1}_x_{feature2}"
                        new_features.append(interaction_name)
                        feature_code.append(f"df['{interaction_name}'] = df['{feature1}'] * df['{feature2}']")

            elif feature_type == "binning":
                for feature in base_features:
                    bin_feature = f"{feature}_binned"
                    new_features.append(bin_feature)
                    feature_code.append(f"df['{bin_feature}'] = pd.cut(df['{feature}'], bins=5, labels=['very_low', 'low', 'medium', 'high', 'very_high'])")

            return {
                "status": "completed",
                "result": {
                    "feature_type": feature_type,
                    "base_features": base_features,
                    "new_features": new_features,
                    "feature_code": feature_code,
                    "total_features_created": len(new_features)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Feature creation failed: {str(e)}"
            }

    async def _select_features(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform feature selection."""
        selection_method = task.get("method", "correlation")
        target_column = task.get("target_column", "")

        try:
            # Mock feature selection results
            all_features = task.get("all_features", [])
            selected_features = all_features[:len(all_features)//2]  # Select half

            feature_scores = {}
            for feature in all_features:
                if feature in selected_features:
                    feature_scores[feature] = round(np.random.uniform(0.6, 0.9), 3)
                else:
                    feature_scores[feature] = round(np.random.uniform(0.1, 0.5), 3)

            return {
                "status": "completed",
                "result": {
                    "selection_method": selection_method,
                    "target_column": target_column,
                    "selected_features": selected_features,
                    "rejected_features": [f for f in all_features if f not in selected_features],
                    "feature_scores": feature_scores,
                    "reduction_percentage": round((1 - len(selected_features)/len(all_features)) * 100, 1)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Feature selection failed: {str(e)}"
            }
