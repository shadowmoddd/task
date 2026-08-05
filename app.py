"""
Мини-сайт для LLM-ассистента исследователя.
Запуск: streamlit run app.py
Требует запущенный `ollama serve` и (опционально) SearXNG на localhost:8080.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import markdown2

from ollama_deep_researcher.graph import graph

# ---------- Настройки страницы ----------
st.set_page_config(page_title="ML Research Assistant", page_icon="🔬", layout="centered")
st.title("🔬 ML Research Assistant")
st.caption("Локальный LLM-ассистент для исследовательских задач в области ML")

# ---------- Боковая панель с настройками ----------
with st.sidebar:
    st.header("Настройки")
    local_llm = st.text_input("Модель Ollama", value="llama3.1:8b")
    search_api = st.selectbox("Поисковик", ["searxng", "duckduckgo"], index=0)
    max_loops = st.slider("Глубина исследования (циклов)", min_value=1, max_value=6, value=3)
    st.caption("Больше циклов → полнее отчёт, но дольше выполнение.")

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

# ---------- Основная форма ----------
query = st.text_area(
    "Введите исследовательский запрос:",
    height=100,
    placeholder="Например: Какие тенденции в развитии LLM имеют место в 2025-2026 году?",
)

run_button = st.button("🚀 Исследовать", type="primary", use_container_width=True)

if run_button:
    if not query.strip():
        st.warning("Введите запрос перед запуском.")
    else:
        config = {
            "configurable": {
                "llm_provider": "ollama",
                "local_llm": local_llm,
                "search_api": search_api,
                "max_web_research_loops": max_loops,
            }
        }

        status_placeholder = st.empty()
        status_placeholder.info("Идёт исследование — генерация запросов, поиск, суммаризация. Это может занять несколько минут...")

        try:
            with st.spinner("Работаю..."):
                result = graph.invoke({"research_topic": query}, config)
            report_md = result["running_summary"]
            status_placeholder.empty()
        except Exception as e:
            status_placeholder.empty()
            st.error(f"Ошибка при выполнении исследования: {e}")
            st.stop()

        st.success("Готово!")
        st.markdown("---")
        st.markdown(report_md)

        # ---------- Сохранение файлов ----------
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"report_{timestamp}"

        md_path = REPORTS_DIR / f"{safe_name}.md"
        md_path.write_text(report_md, encoding="utf-8")

        html_body = markdown2.markdown(report_md, extras=["tables", "fenced-code-blocks"])
        html_full = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Research Report</title>
<style>
body {{ font-family: -apple-system, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
h1, h2, h3 {{ color: #1a1a1a; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
        html_path = REPORTS_DIR / f"{safe_name}.html"
        html_path.write_text(html_full, encoding="utf-8")

        # ---------- Кнопки скачивания ----------
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 Скачать .md",
                data=report_md,
                file_name=f"{safe_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "🌐 Скачать .html",
                data=html_full,
                file_name=f"{safe_name}.html",
                mime="text/html",
                use_container_width=True,
            )

        st.caption(f"Отчёт также сохранён локально в {md_path}")