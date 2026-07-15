import os
import re
import pandas as pd
from typing import List, Dict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_customer_service.config import settings


class ChatDataCleaner:
    """电商聊天数据清洗器（完全独立）"""

    def __init__(self):
        self.sensitive_words = ["密码", "验证码", "身份证", "银行卡", "支付宝"]
        self.useless_patterns = [
            r"^\s*$",
            r"^系统消息[：:].*",
            r"^\[.*\]$",
        ]

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """完整清洗流程"""
        print(f"📊 原始数据: {len(df)} 条")
        df = self._drop_duplicates(df)
        df = self._filter_useless(df)
        df = self._remove_sensitive(df)
        df = self._standardize_format(df)
        df = self._extract_intent(df)
        print(f"✅ 清洗后: {len(df)} 条")
        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        if "message" in df.columns and "user_id" in df.columns:
            df = df.drop_duplicates(subset=["user_id", "message"], keep="first")
        elif "message" in df.columns:
            df = df.drop_duplicates(subset=["message"], keep="first")
        print(f"  去重: {before} → {len(df)}")
        return df

    def _filter_useless(self, df: pd.DataFrame) -> pd.DataFrame:
        if "message" not in df.columns:
            return df
        before = len(df)
        pattern = re.compile("|".join(self.useless_patterns))
        df = df[~df["message"].apply(lambda x: bool(pattern.match(str(x).strip())))]
        print(f"  过滤无用: {before} → {len(df)}")
        return df

    def _remove_sensitive(self, df: pd.DataFrame) -> pd.DataFrame:
        if "message" not in df.columns:
            return df

        def mask(msg):
            if not isinstance(msg, str):
                return msg
            for word in self.sensitive_words:
                if word in msg:
                    msg = msg.replace(word, "***")
            return msg

        df["message"] = df["message"].apply(mask)
        return df

    def _standardize_format(self, df: pd.DataFrame) -> pd.DataFrame:
        if "message" not in df.columns:
            return df

        def normalize(text):
            if not isinstance(text, str):
                return text
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"([。！？])\1+", r"\1", text)
            return text.strip()

        df["message"] = df["message"].apply(normalize)
        return df

    def _extract_intent(self, df: pd.DataFrame) -> pd.DataFrame:
        if "message" not in df.columns:
            return df

        def classify(text):
            if not isinstance(text, str):
                return "other"
            if any(kw in text for kw in ["价格", "多少钱", "便宜", "贵"]):
                return "price"
            if any(kw in text for kw in ["售后", "退货", "退款", "维修"]):
                return "after_sales"
            if any(kw in text for kw in ["发货", "物流", "快递", "多久到"]):
                return "logistics"
            if any(kw in text for kw in ["质量", "好用", "效果"]):
                return "quality"
            return "general"

        df["intent"] = df["message"].apply(classify)
        return df


def load_sample_data() -> pd.DataFrame:
    """生成示例数据"""
    return pd.DataFrame([
        {"user_id": "u1001", "message": "这个商品多少钱？", "time": "2026-07-01 10:00:00"},
        {"user_id": "u1001", "message": "能便宜点吗", "time": "2026-07-01 10:01:00"},
        {"user_id": "u1002", "message": "我要退货", "time": "2026-07-01 10:05:00"},
        {"user_id": "u1003", "message": "物流怎么查", "time": "2026-07-01 10:10:00"},
        {"user_id": "u1001", "message": "密码是123456", "time": "2026-07-01 10:03:00"},
        {"user_id": "u1004", "message": "", "time": "2026-07-01 10:15:00"},
    ])


if __name__ == "__main__":
    settings.ensure_dirs()
    df = load_sample_data()
    print("原始数据:")
    print(df.to_string())

    cleaner = ChatDataCleaner()
    cleaned_df = cleaner.clean(df)

    output_path = os.path.join(settings.CLEANED_DATA_DIR, "sample_cleaned.csv")
    cleaned_df.to_csv(output_path, index=False)
    print(f"\n✅ 已保存到: {output_path}")