"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import streamlit as st
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: 検索結果のDocumentオブジェクトのリスト
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # 検索結果から最も関連性の高い商品を取得
    if not result or len(result) == 0:
        st.error("商品情報が見つかりませんでした。")
        return
    
    # 最初の検索結果から商品情報を取得
    product_content = result[0].page_content
    product_lines = product_content.split("\n")
    
    # 商品情報を辞書に変換
    product = {}
    for line in product_lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            # BOM文字を削除
            key = key.replace('\ufeff', '')
            product[key] = value

    # 必要なキーが存在するかチェック
    required_keys = ['name', 'id', 'price', 'category', 'maker', 'score', 'review_number', 'file_name', 'description', 'recommended_people']
    missing_keys = [key for key in required_keys if key not in product]
    
    if missing_keys:
        st.error(f"商品情報に不足があります: {', '.join(missing_keys)}")
        st.code(f"取得した商品情報:\n{product_content}", language=None)
        return

    st.markdown("以下の商品をご提案いたします。")

    # 「商品名」と「価格」
    st.success(f"""
            商品名：{product['name']}（商品ID: {product['id']}）\n
            価格：{product['price']}
    """)

    # 「商品カテゴリ」と「メーカー」と「ユーザー評価」
    st.code(f"""
        商品カテゴリ：{product['category']}\n
        メーカー：{product['maker']}\n
        評価：{product['score']}({product['review_number']}件)
    """, language=None, wrap_lines=True)

    # 商品画像
    image_path = f"./images/products/{product['file_name']}"
    try:
        st.image(image_path, width=400)
    except Exception as e:
        st.warning(f"商品画像を読み込めませんでした: {image_path}")
        logger.warning(f"画像読み込みエラー: {e}")

    # 商品説明
    st.code(product['description'], language=None, wrap_lines=True)

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product["recommended_people"])

    # 商品ページのリンク
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")