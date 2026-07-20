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
    "meipingbao",
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

    def test_required_sections_and_removed_duplicate_section(self) -> None:
        for heading in (
            "## 🆕 New: NoiseFilter",
            "## ⭐ Featured projects",
            "## 🤖 AI Products",
            "## 🧩 Agent Skills & Content Workflows",
        ):
            self.assertIn(heading, ENGLISH)
        for heading in (
            "## 🆕 最新：NoiseFilter",
            "## ⭐ 精选项目",
            "## 🤖 AI 产品",
            "## 🧩 Agent Skills 与内容工作流",
        ):
            self.assertIn(heading, CHINESE)
        self.assertNotIn("Content & Growth Tools", ENGLISH)
        self.assertNotIn("内容与增长工具", CHINESE)

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
