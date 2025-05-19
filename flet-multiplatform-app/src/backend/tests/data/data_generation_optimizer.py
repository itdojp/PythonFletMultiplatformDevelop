"""高度なデータ生成最適化モジュール"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Type

import numpy as np
import pandas as pd
from scipy.stats import norm

from ..data.data_generator_optimized import DataGeneratorOptimized
from ..environment.performance_optimizer import PerformanceOptimizer
from ..validation.validation_rules import ValidationRuleBuilder


class GenerationStrategy(Enum):
    """生成戦略"""

    RANDOM = "random"
    SEQUENTIAL = "sequential"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"
    PERFORMANCE = "performance"


class GenerationPattern(Enum):
    """生成パターン"""

    NORMAL = "normal"
    UNIFORM = "uniform"
    EXPONENTIAL = "exponential"
    BETA = "beta"
    GAMMA = "gamma"


@dataclass
class GenerationConfig:
    """生成設定データクラス"""

    strategy: GenerationStrategy
    pattern: GenerationPattern
    distribution_params: Dict[str, Any]
    correlation_matrix: Optional[np.ndarray] = None
    batch_size: int = 100
    max_workers: int = 4


class DataGenerationOptimizer:
    """データ生成最適化クラス"""

    def __init__(self):
        """初期化"""
        self.data_generator = DataGeneratorOptimized()
        self.validation_builder = ValidationRuleBuilder()
        self.performance_optimizer = PerformanceOptimizer()
        self.executor = ThreadPoolExecutor()

    def optimize_generation(
        self, data_type: str, count: int, config: GenerationConfig
    ) -> List[Dict[str, Any]]:
        """データ生成を最適化

        Args:
            data_type (str): データタイプ
            count (int): 生成するデータ数
            config (GenerationConfig): 生成設定

        Returns:
            List[Dict[str, Any]]: 最適化されたデータ
        """
        optimized_data = []

        # バッチ処理の設定
        batch_size = min(config.batch_size, count)
        num_batches = (count + batch_size - 1) // batch_size

        # パラレル生成の設定
        max_workers = min(config.max_workers, num_batches)

        # データ生成の最適化
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, count)

            # データ生成戦略の選択
            if config.strategy == GenerationStrategy.RANDOM:
                batch = self._generate_random(
                    data_type,
                    end_idx - start_idx,
                    config.pattern,
                    config.distribution_params,
                )
            elif config.strategy == GenerationStrategy.SEQUENTIAL:
                batch = self._generate_sequential(
                    data_type,
                    end_idx - start_idx,
                    config.pattern,
                    config.distribution_params,
                )
            elif config.strategy == GenerationStrategy.DISTRIBUTION:
                batch = self._generate_with_distribution(
                    data_type,
                    end_idx - start_idx,
                    config.pattern,
                    config.distribution_params,
                    config.correlation_matrix,
                )
            elif config.strategy == GenerationStrategy.CORRELATION:
                batch = self._generate_with_correlation(
                    data_type,
                    end_idx - start_idx,
                    config.pattern,
                    config.distribution_params,
                    config.correlation_matrix,
                )
            elif config.strategy == GenerationStrategy.PERFORMANCE:
                batch = self._generate_with_performance(
                    data_type,
                    end_idx - start_idx,
                    config.pattern,
                    config.distribution_params,
                )

            optimized_data.extend(batch)

        return optimized_data

    def _generate_random(
        self,
        data_type: str,
        count: int,
        pattern: GenerationPattern,
        params: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """ランダムデータ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            pattern (GenerationPattern): 生成パターン
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        if pattern == GenerationPattern.NORMAL:
            data = self._generate_normal(data_type, count, params)
        elif pattern == GenerationPattern.UNIFORM:
            data = self._generate_uniform(data_type, count, params)
        elif pattern == GenerationPattern.EXPONENTIAL:
            data = self._generate_exponential(data_type, count, params)
        elif pattern == GenerationPattern.BETA:
            data = self._generate_beta(data_type, count, params)
        elif pattern == GenerationPattern.GAMMA:
            data = self._generate_gamma(data_type, count, params)

        return data

    def _generate_sequential(
        self,
        data_type: str,
        count: int,
        pattern: GenerationPattern,
        params: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """連番データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            pattern (GenerationPattern): 生成パターン
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.SEQUENTIAL, params
            )[0]
            data.append(item)
        return data

    def _generate_with_distribution(
        self,
        data_type: str,
        count: int,
        pattern: GenerationPattern,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """分布に基づくデータ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            pattern (GenerationPattern): 生成パターン
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        if pattern == GenerationPattern.NORMAL:
            data = self._generate_normal_with_correlation(
                data_type, count, params, correlation_matrix
            )
        elif pattern == GenerationPattern.UNIFORM:
            data = self._generate_uniform_with_correlation(
                data_type, count, params, correlation_matrix
            )
        elif pattern == GenerationPattern.EXPONENTIAL:
            data = self._generate_exponential_with_correlation(
                data_type, count, params, correlation_matrix
            )
        elif pattern == GenerationPattern.BETA:
            data = self._generate_beta_with_correlation(
                data_type, count, params, correlation_matrix
            )
        elif pattern == GenerationPattern.GAMMA:
            data = self._generate_gamma_with_correlation(
                data_type, count, params, correlation_matrix
            )

        return data

    def _generate_with_correlation(
        self,
        data_type: str,
        count: int,
        pattern: GenerationPattern,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """相関に基づくデータ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            pattern (GenerationPattern): 生成パターン
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        if correlation_matrix is None:
            return self._generate_with_distribution(
                data_type, count, pattern, params, None
            )

        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.COMBINED, params
            )[0]
            data.append(item)

        # 相関行列に基づく調整
        df = pd.DataFrame(data)
        corr = df.corr()
        if not np.allclose(corr, correlation_matrix, atol=0.1):
            # 相関が目標と異なる場合は調整
            adjusted = self._adjust_correlation(df, correlation_matrix)
            data = adjusted.to_dict("records")

        return data

    def _generate_with_performance(
        self,
        data_type: str,
        count: int,
        pattern: GenerationPattern,
        params: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """パフォーマンス考慮のデータ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            pattern (GenerationPattern): 生成パターン
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.RANDOM, params
            )[0]

            # パフォーマンス最適化
            optimized = self.performance_optimizer.optimize_data(
                [item], self.validation_builder.get_validation_rules(data_type)
            )[0]
            data.append(optimized)

        return data

    def _generate_normal(
        self, data_type: str, count: int, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """正規分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        mean = params.get("mean", 0)
        std = params.get("std", 1)

        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.RANDOM
            )[0]

            # 正規分布に基づく調整
            for field, value in item.items():
                if isinstance(value, (int, float)):
                    item[field] = norm.ppf(random(), loc=mean, scale=std)

            data.append(item)

        return data

    def _generate_uniform(
        self, data_type: str, count: int, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """一様分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        low = params.get("low", 0)
        high = params.get("high", 1)

        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.RANDOM
            )[0]

            # 一様分布に基づく調整
            for field, value in item.items():
                if isinstance(value, (int, float)):
                    item[field] = random() * (high - low) + low

            data.append(item)

        return data

    def _generate_exponential(
        self, data_type: str, count: int, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """指数分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        scale = params.get("scale", 1)

        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.RANDOM
            )[0]

            # 指数分布に基づく調整
            for field, value in item.items():
                if isinstance(value, (int, float)):
                    item[field] = -np.log(1 - random()) * scale

            data.append(item)

        return data

    def _generate_beta(
        self, data_type: str, count: int, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ベータ分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        alpha = params.get("alpha", 2)
        beta = params.get("beta", 5)

        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.RANDOM
            )[0]

            # ベータ分布に基づく調整
            for field, value in item.items():
                if isinstance(value, (int, float)):
                    item[field] = random() ** (1 / alpha) * (1 - random()) ** (1 / beta)

            data.append(item)

        return data

    def _generate_gamma(
        self, data_type: str, count: int, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """ガンマ分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        shape = params.get("shape", 2)
        scale = params.get("scale", 1)

        data = []
        for i in range(count):
            item = self.data_generator.generate_test_data_batch(
                data_type, 1, DataGenerationType.RANDOM
            )[0]

            # ガンマ分布に基づく調整
            for field, value in item.items():
                if isinstance(value, (int, float)):
                    item[field] = np.random.gamma(shape, scale)

            data.append(item)

        return data

    def _generate_normal_with_correlation(
        self,
        data_type: str,
        count: int,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """相関のある正規分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        mean = params.get("mean", 0)
        std = params.get("std", 1)

        if correlation_matrix is not None:
            # 相関行列に基づくデータ生成
            cov = np.diag(std) @ correlation_matrix @ np.diag(std)
            data = np.random.multivariate_normal(
                mean=np.full(len(params), mean), cov=cov, size=count
            )
        else:
            # 単純な正規分布データ生成
            data = np.random.normal(loc=mean, scale=std, size=(count, len(params)))

        return [dict(zip(params.keys(), row)) for row in data]

    def _generate_uniform_with_correlation(
        self,
        data_type: str,
        count: int,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """相関のある一様分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        low = params.get("low", 0)
        high = params.get("high", 1)

        if correlation_matrix is not None:
            # 相関行列に基づくデータ生成
            data = np.random.uniform(low=low, high=high, size=(count, len(params)))
            # 相関を適用
            data = data @ np.linalg.cholesky(correlation_matrix)
        else:
            # 単純な一様分布データ生成
            data = np.random.uniform(low=low, high=high, size=(count, len(params)))

        return [dict(zip(params.keys(), row)) for row in data]

    def _generate_exponential_with_correlation(
        self,
        data_type: str,
        count: int,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """相関のある指数分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        scale = params.get("scale", 1)

        if correlation_matrix is not None:
            # 相関行列に基づくデータ生成
            data = -np.log(1 - np.random.uniform(size=(count, len(params)))) * scale
            # 相関を適用
            data = data @ np.linalg.cholesky(correlation_matrix)
        else:
            # 単純な指数分布データ生成
            data = -np.log(1 - np.random.uniform(size=(count, len(params)))) * scale

        return [dict(zip(params.keys(), row)) for row in data]

    def _generate_beta_with_correlation(
        self,
        data_type: str,
        count: int,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """相関のあるベータ分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        alpha = params.get("alpha", 2)
        beta = params.get("beta", 5)

        if correlation_matrix is not None:
            # 相関行列に基づくデータ生成
            data = np.random.beta(alpha=alpha, beta=beta, size=(count, len(params)))
            # 相関を適用
            data = data @ np.linalg.cholesky(correlation_matrix)
        else:
            # 単純なベータ分布データ生成
            data = np.random.beta(alpha=alpha, beta=beta, size=(count, len(params)))

        return [dict(zip(params.keys(), row)) for row in data]

    def _generate_gamma_with_correlation(
        self,
        data_type: str,
        count: int,
        params: Dict[str, Any],
        correlation_matrix: Optional[np.ndarray],
    ) -> List[Dict[str, Any]]:
        """相関のあるガンマ分布データ生成

        Args:
            data_type (str): データタイプ
            count (int): 生成数
            params (Dict[str, Any]): パラメータ
            correlation_matrix (Optional[np.ndarray]): 相関行列

        Returns:
            List[Dict[str, Any]]: 生成されたデータ
        """
        shape = params.get("shape", 2)
        scale = params.get("scale", 1)

        if correlation_matrix is not None:
            # 相関行列に基づくデータ生成
            data = np.random.gamma(shape=shape, scale=scale, size=(count, len(params)))
            # 相関を適用
            data = data @ np.linalg.cholesky(correlation_matrix)
        else:
            # 単純なガンマ分布データ生成
            data = np.random.gamma(shape=shape, scale=scale, size=(count, len(params)))

        return [dict(zip(params.keys(), row)) for row in data]

    def _adjust_correlation(
        self, df: pd.DataFrame, target_corr: np.ndarray
    ) -> pd.DataFrame:
        """相関を調整

        Args:
            df (pd.DataFrame): 調整対象のデータフレーム
            target_corr (np.ndarray): 目標の相関行列

        Returns:
            pd.DataFrame: 相関が調整されたデータフレーム
        """
        current_corr = df.corr()
        adjustment = target_corr - current_corr

        for col in df.columns:
            for other_col in df.columns:
                if col != other_col:
                    df[col] += adjustment[col][other_col] * df[other_col]

        return df
