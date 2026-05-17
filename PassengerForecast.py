import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

class PassengerForecast:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.features = [
            'avg_temp_c', 'is_weekday', 'special_event',
            'train_frequency', 'ticket_price'
        ]
        self.target = 'daily_passengers'
        # Используем numpy-массивы без имён признаков, чтобы избежать предупреждений
        self.X = self.df[self.features].values
        self.y = self.df[self.target].values
        self.models = {}   # {degree: (model, r2, formula_str)}

    def train_models(self):
        """Обучает линейную (degree=1) и полиномиальные (2, 3) модели."""
        for degree in [1, 2, 3]:
            if degree == 1:
                model = LinearRegression()
                model.fit(self.X, self.y)
                y_pred = model.predict(self.X)
                r2 = r2_score(self.y, y_pred)
                # Формула линейной модели
                coef = model.coef_
                intercept = model.intercept_
                terms = [f"{coef[i]:.4f}*{self.features[i]}" for i in range(len(self.features))]
                formula = f"y = {intercept:.4f} + " + " + ".join(terms)
            else:
                # Пайплайн с полиномиальными признаками
                model = make_pipeline(
                    PolynomialFeatures(degree=degree, include_bias=False),
                    LinearRegression()
                )
                model.fit(self.X, self.y)
                y_pred = model.predict(self.X)
                r2 = r2_score(self.y, y_pred)
                # Извлекаем коэффициенты линейной регрессии внутри пайплайна
                linear = model.named_steps['linearregression']
                poly = model.named_steps['polynomialfeatures']
                coeffs = linear.coef_
                intercept = linear.intercept_
                feature_names = poly.get_feature_names_out(self.features)
                # Ограничим первые 8 слагаемых для читаемой формулы
                n_terms = min(8, len(coeffs))
                terms = [f"{coeffs[i]:.4f}*{feature_names[i]}" for i in range(n_terms)]
                formula = f"y = {intercept:.4f} + " + " + ".join(terms) + " + ..."
            
            self.models[degree] = (model, r2, formula)
            # print(f"Степень {degree}: R² = {r2:.4f}")

    def predict(self, degree, avg_temp_c, is_weekday, special_event, train_frequency, ticket_price):
        """Прогноз для заданной степени модели."""
        model, _, _ = self.models[degree]
        # Формируем numpy-массив из 1 строки
        X_new = np.array([[avg_temp_c, is_weekday, special_event, train_frequency, ticket_price]])
        if model.predict(X_new)[0] < 0 :
            return 0
        else: return model.predict(X_new)[0]