import random
import uvicorn
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import RedirectResponse


# --------------------------------------------------------------------------
# 1. 三個 Gradio 介面：Home / Constitution / Food
# --------------------------------------------------------------------------
def build_home_page() -> gr.Blocks:
    with gr.Blocks(title="食物寒熱辨識") as home:
        gr.Markdown("# 食物寒熱辨識")
        gr.Markdown("請選擇功能：")
        with gr.Row():
            gr.Button("體質測試", link="/constitution")
            gr.Button("食物辨識", link="/food")
    return home


def build_constitution_page() -> gr.Blocks:
    QUESTIONS = [
        ("您平時容易手腳冰冷嗎？", ["是", "否", "偶爾"]),
        ("您飲食口味偏好？", ["清淡", "重口味", "無所謂"]),
        ("您常常感到喉嚨乾燥嗎？", ["是", "否", "偶爾"]),
    ]
    answer_sets: list[tuple[str, list[str]]] = []

    def collect_answers(*ans):
        answer_sets.append(set(ans))
        return f"✅ 已收到，現在共有 {len(answer_sets)} 份紀錄。"

    with gr.Blocks(title="體質測試") as page:
        gr.Markdown("## 體質測試表單")
        radios = [gr.Radio(opts, label=q) for q, opts in QUESTIONS]
        gr.Button("提交").click(collect_answers, radios, gr.Textbox(interactive=False))
        gr.Button("回到首頁", link="/home", size="sm")
    return page


def build_food_page() -> gr.Blocks:
    def classify(img):
        return {"五性結果": random.choice(["寒性", "涼性", "平性", "溫性", "熱性"])}

    with gr.Blocks(title="食物辨識") as page:
        gr.Markdown("## 食物辨識")
        img = gr.Image(type="pil", label="請上傳食物照片")
        img.change(classify, img, gr.Label(num_top_classes=1))
        gr.Button("回到首頁", link="/home", size="sm")
    return page


# --------------------------------------------------------------------------
# 2. 掛到 FastAPI —— 注意 **沒有** 任何 Gradio 介面掛在 "/"
# --------------------------------------------------------------------------
app = FastAPI()

# 子頁面
app = gr.mount_gradio_app(app, build_constitution_page(), path="/constitution")
app = gr.mount_gradio_app(app, build_food_page(), path="/food")

# 首頁掛在 /home
app = gr.mount_gradio_app(app, build_home_page(), path="/home")


# 根目錄只做轉址，避免吃掉其他路由
@app.get("/", include_in_schema=False)
async def _root():
    return RedirectResponse(url="/home")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
