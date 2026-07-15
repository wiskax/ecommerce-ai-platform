import json
import pandas as pd
from pathlib import Path


class AnnotationTool:
    """
    人工标注工具
    对清洗后的聊天数据进行标注
    """

    def __init__(self, data_path: str):
        self.df = pd.read_csv(data_path)
        self.annotations = []
        self.current_index = 0
        self.output_dir = "./data/annotated"

        # 确保输出目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # 加载已保存的进度
        self.progress_file = f"{self.output_dir}/progress.json"
        self._load_progress()

    def _load_progress(self):
        """加载之前的标注进度"""
        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                self.annotations = saved.get("annotations", [])
                self.current_index = saved.get("last_index", 0)
                print(f"✅ 加载进度: 已标注 {len(self.annotations)} 条，当前在第 {self.current_index + 1} 条")
        except FileNotFoundError:
            print("📝 开始新标注任务")

    def _save_progress(self):
        """保存进度"""
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump({
                "annotations": self.annotations,
                "last_index": self.current_index
            }, f, ensure_ascii=False, indent=2)

    def start(self):
        """启动标注交互"""
        total = len(self.df)
        print(f"\n🧠 开始人工标注 (共 {total} 条)")
        print("标注选项:")
        print("  1 - 有效 FAQ（问答对）")
        print("  2 - 无效（不加入知识库）")
        print("  3 - 需补充答案")
        print("  4 - 跳过")
        print("  0 - 保存并退出\n")

        for idx in range(self.current_index, total):
            self.current_index = idx
            row = self.df.iloc[idx]

            print(f"\n--- 第 {idx+1}/{total} 条 ---")
            print(f"用户: {row.get('user_id', 'unknown')}")
            print(f"消息: {row.get('message', '')}")
            if 'intent' in row:
                print(f"意图: {row.get('intent', 'unknown')}")

            choice = self._get_choice()

            if choice == "0":
                self._save_progress()
                print("\n💾 已保存进度，退出")
                break

            if choice == "4":
                self._save_progress()
                continue

            # 处理标注
            status_map = {"1": "faq", "2": "invalid", "3": "need_supplement"}
            label = status_map.get(choice, "unknown")

            annotation = {
                "original": row.to_dict(),
                "label": label,
                "index": idx
            }

            # 如果是 FAQ，补充答案
            if choice == "1":
                print("\n请输入标准答案（作为 FAQ 的回答）:")
                answer = input("答案: ").strip()
                if answer:
                    annotation["answer"] = answer
                else:
                    print("⚠️ 未输入答案，跳过此条")
                    continue

            self.annotations.append(annotation)
            self._save_progress()
            print(f"✅ 已标注: {label}")

        self._export()
        print(f"\n🎉 标注完成！共标注 {len(self.annotations)} 条")
        print(f"📁 结果保存在: {self.output_dir}")

    def _get_choice(self) -> str:
        """获取用户选择"""
        while True:
            choice = input("选择 (1-FAQ 2-无效 3-补充 4-跳过 0-退出): ").strip()
            if choice in ["0", "1", "2", "3", "4"]:
                return choice
            print("❌ 请输入 0-4")

    def _export(self):
        """导出标注结果"""
        if not self.annotations:
            print("⚠️ 没有标注数据可导出")
            return

        # 导出所有标注
        df_all = pd.DataFrame(self.annotations)
        df_all.to_csv(f"{self.output_dir}/all_annotations.csv", index=False)
        print(f"✅ 导出全部标注: {len(self.annotations)} 条 -> {self.output_dir}/all_annotations.csv")

        # 导出 FAQ（有效问答对）
        faqs = [a for a in self.annotations if a.get("label") == "faq" and a.get("answer")]
        if faqs:
            df_faqs = pd.DataFrame(faqs)
            # 提取问答对
            faq_data = []
            for f in faqs:
                original = f.get("original", {})
                faq_data.append({
                    "question": original.get("message", ""),
                    "answer": f.get("answer", ""),
                    "intent": original.get("intent", "general"),
                    "user_id": original.get("user_id", "")
                })
            df_faq = pd.DataFrame(faq_data)
            df_faq.to_csv(f"{self.output_dir}/faqs.csv", index=False)
            print(f"✅ 导出 FAQ: {len(faqs)} 条 -> {self.output_dir}/faqs.csv")

        # 导出需要补充的
        need_supplement = [a for a in self.annotations if a.get("label") == "need_supplement"]
        if need_supplement:
            df_supp = pd.DataFrame(need_supplement)
            df_supp.to_csv(f"{self.output_dir}/need_supplement.csv", index=False)
            print(f"⚠️ 需要补充的: {len(need_supplement)} 条 -> {self.output_dir}/need_supplement.csv")


if __name__ == "__main__":
    # 确保数据目录存在
    Path("data/cleaned").mkdir(parents=True, exist_ok=True)
    Path("data/annotated").mkdir(parents=True, exist_ok=True)

    # 检查清洗后的数据是否存在
    cleaned_file = "data/cleaned/sample_cleaned.csv"
    if not Path(cleaned_file).exists():
        print(f"⚠️ 文件不存在: {cleaned_file}")
        print("请先运行 cleaner.py 生成清洗数据")
        exit()

    # 启动标注
    tool = AnnotationTool(cleaned_file)
    tool.start()