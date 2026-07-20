from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGLISH = (ROOT / "README.md").read_text(encoding="utf-8")
CHINESE = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

EXPECTED_REPOSITORIES = [
    "content-curation",
    "YiShu-Workbench",
    "ai-speaking-coach",
    "claude-skills",
    "GZHcomposing",
    "yishu5skill",
    "feishu-imghost",
]
FEATURED_REPOSITORIES = [
    "GZHcomposing",
    "claude-skills",
    "YiShu-Workbench",
    "content-curation",
]


class ProfileReadmeTest(unittest.TestCase):
    def test_language_navigation(self) -> None:
        self.assertIn("**English** · [中文](README.zh-CN.md)", ENGLISH)
        self.assertIn("[English](README.md) · **中文**", CHINESE)

    def test_personal_positioning(self) -> None:
        self.assertIn(
            "**I turn frontline business problems into practical AI products.**",
            ENGLISH,
        )
        self.assertIn(
            "**我把一线业务中的真实问题，做成真正可用的 AI 产品。**",
            CHINESE,
        )
        self.assertIn("reducing information noise", ENGLISH)
        self.assertIn("降低信息噪音", CHINESE)

    def test_required_sections_and_removed_duplicate_section(self) -> None:
        for heading in (
            "## 🧭 From frontline to product",
            "## 🆕 New: NoiseFilter",
            "## ⭐ Featured projects",
            "## 🤖 AI Products",
            "## 🧩 Agent Skills & Content Workflows",
        ):
            self.assertIn(heading, ENGLISH)
        for heading in (
            "## 🧭 从业务现场到 AI 产品",
            "## 🆕 最新：NoiseFilter",
            "## ⭐ 精选项目",
            "## 🤖 AI 产品",
            "## 🧩 Agent Skills 与内容工作流",
        ):
            self.assertIn(heading, CHINESE)
        self.assertNotIn("Content & Growth Tools", ENGLISH)
        self.assertNotIn("内容与增长工具", CHINESE)

    def test_frontline_section_order_and_public_links(self) -> None:
        for text, heading, next_heading in (
            (ENGLISH, "## 🧭 From frontline to product", "## 🆕 New: NoiseFilter"),
            (CHINESE, "## 🧭 从业务现场到 AI 产品", "## 🆕 最新：NoiseFilter"),
        ):
            csdn_position = text.index("✍️ [CSDN]")
            section_position = text.index(heading)
            next_position = text.index(next_heading)
            self.assertLess(csdn_position, section_position)
            self.assertLess(section_position, next_position)
            section = text[section_position:next_position]
            for repo in ("content-curation", "YiShu-Workbench", "GZHcomposing"):
                self.assertIn(f"https://github.com/YiShu5/{repo}", section)

    def test_meipingbao_is_private_product_not_link(self) -> None:
        for text, label in (
            (ENGLISH, "**Meipingbao** *(private prototype)*"),
            (CHINESE, "**Meipingbao**（私有原型）"),
        ):
            self.assertIn(label, text)
            self.assertNotIn("https://github.com/YiShu5/meipingbao", text)

    def test_expected_repository_links_exist_in_both_languages(self) -> None:
        for repo in EXPECTED_REPOSITORIES:
            url = f"https://github.com/YiShu5/{repo}"
            self.assertIn(url, ENGLISH)
            self.assertIn(url, CHINESE)

    def test_featured_star_markers_match(self) -> None:
        pattern = re.compile(r"<!--stars:([A-Za-z0-9_.-]+)-->")
        self.assertEqual(FEATURED_REPOSITORIES, pattern.findall(ENGLISH))
        self.assertEqual(FEATURED_REPOSITORIES, pattern.findall(CHINESE))

    def test_featured_order(self) -> None:
        for text, heading in (
            (ENGLISH, "## ⭐ Featured projects"),
            (CHINESE, "## ⭐ 精选项目"),
        ):
            featured = text.split(heading, 1)[1].split("\n---", 1)[0]
            positions = [
                featured.index(f"https://github.com/YiShu5/{repo}")
                for repo in FEATURED_REPOSITORIES
            ]
            self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
