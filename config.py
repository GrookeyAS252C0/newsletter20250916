"""
設定とデータクラス
"""

import os
from dataclasses import dataclass
from datetime import date
from typing import Optional

# USER_AGENT環境変数を早期に設定
if not os.getenv("USER_AGENT"):
    os.environ["USER_AGENT"] = "Newsletter-Generator/1.0 (Educational-Purpose)"

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("pydanticがインストールされていません: pip install pydantic")


@dataclass
class AppConfig:
    """アプリケーション設定"""
    openai_api_key: str
    youtube_api_key: Optional[str]
    user_agent: str = "Newsletter-Generator/1.0 (Educational-Purpose)"
    youtube_channel_handle: str = "nichidaiichi"
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """環境変数から設定を読み込み"""
        user_agent = os.getenv("USER_AGENT", "Newsletter-Generator/1.0 (Educational-Purpose)")
        
        # Streamlit Cloudの場合はst.secretsから取得
        try:
            import streamlit as st
            openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
            youtube_api_key = st.secrets.get("YOUTUBE_API_KEY", os.getenv("YOUTUBE_API_KEY"))
        except:
            openai_api_key = os.getenv("OPENAI_API_KEY", "")
            youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        
        return cls(
            openai_api_key=openai_api_key,
            youtube_api_key=youtube_api_key,
            user_agent=user_agent,
        )


class WeatherInfo(BaseModel):
    """天気情報のデータ構造（時間帯別登校・授業終了情報対応）"""
    # 登校時間（8時）の情報
    登校時_天気: str = Field(description="8時頃の天気（例：晴れ、曇り、雨）")
    登校時_最高気温: str = Field(description="日中の最高気温（例：25度）")
    登校時_最低気温: str = Field(description="朝の最低気温（例：18度）")
    登校時_降水確率: str = Field(description="8時頃の降水確率（例：10%）")
    登校時_湿度: str = Field(description="8時頃の湿度（例：65%）")
    登校時_風速風向: str = Field(description="8時頃の風（例：南西の風3m/s）")

    # 授業終了時間の情報（曜日により異なる）
    授業終了時_天気: str = Field(description="授業終了時の天気（例：晴れ、曇り、雨）")
    授業終了時_気温: str = Field(description="授業終了時の気温（例：23度）")
    授業終了時_降水確率: str = Field(description="授業終了時の降水確率（例：20%）")
    授業終了時_湿度: str = Field(description="授業終了時の湿度（例：60%）")
    授業終了時_風速風向: str = Field(description="授業終了時の風（例：西の風2m/s）")
    授業終了時刻: str = Field(description="授業終了時刻（例：15時、14時、12時30分）")

    # 全日の概要
    天気概況: str = Field(description="一日の天気概況（例：晴れ時々曇り）")
    快適具合: str = Field(description="過ごしやすさの評価（例：過ごしやすい、蒸し暑い、肌寒い）")
    月齢: str = Field(description="月の満ち欠けの状態（例：新月、上弦の月、満月、下弦の月）", default="")
    気圧状況: str = Field(description="気圧の状況（例：高気圧、低気圧、気圧の谷、気圧変化なし）", default="")


class PressureInfo(BaseModel):
    """気圧情報のデータ構造"""
    現在気圧: str = Field(description="現在の気圧値（例：1013.2hPa）")
    気圧変化: str = Field(description="気圧の変化傾向（例：下降中、上昇中、安定）")
    変化量: str = Field(description="気圧変化量（例：-2.1hPa/3h）", default="")
    気圧予測: str = Field(description="今後の気圧予測（例：さらに下降予想、安定継続）")
    気圧レベル: str = Field(description="気圧の高低評価（例：やや低め、標準、高め）")
    体調影響: str = Field(description="気圧による体調への影響予測（例：頭痛注意、良好、集中力低下の可能性）", default="")


@dataclass
class YouTubeVideo:
    """YouTube動画情報"""
    title: str
    url: str
    published_at: str
    thumbnail: str
    channel_title: str
    matched_query: str


@dataclass
class EventInfo:
    """イベント情報"""
    date: date
    event: str
    date_str: str