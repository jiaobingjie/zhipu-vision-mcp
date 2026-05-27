import os
import pytest
from unittest.mock import patch, MagicMock


class TestGetClient:
    def test_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ZHIPUAI_API_KEY"):
                from zhipu_vision_mcp.server import get_client
                get_client()

    def test_valid_api_key(self):
        with patch.dict(os.environ, {"ZHIPUAI_API_KEY": "test-key"}):
            from zhipu_vision_mcp.server import get_client
            client = get_client()
            assert client is not None


class TestEncodeFile:
    def test_file_not_found(self, tmp_path):
        from zhipu_vision_mcp.server import encode_file
        with pytest.raises(ValueError, match="File not found"):
            encode_file(str(tmp_path / "nonexistent.png"))

    def test_unsupported_file_type(self, tmp_path):
        from zhipu_vision_mcp.server import encode_file
        f = tmp_path / "test.xyz"
        f.write_bytes(b"\x00")
        with pytest.raises(ValueError, match="Unsupported file type"):
            encode_file(str(f))

    def test_valid_image(self, tmp_path):
        from zhipu_vision_mcp.server import encode_file
        f = tmp_path / "test.png"
        f.write_bytes(b"\x89PNG\r\n")
        b64, mime = encode_file(str(f))
        assert mime == "image/png"
        assert isinstance(b64, str)


class TestVideoSizeLimit:
    def test_video_exceeds_size_limit(self, tmp_path):
        from zhipu_vision_mcp.server import analyze_video
        f = tmp_path / "big.mp4"
        f.write_bytes(b"\x00" * (9 * 1024 * 1024))
        with pytest.raises(ValueError, match="exceeds 8MB limit"):
            analyze_video(str(f), "test")

    def test_video_within_size_limit(self, tmp_path):
        from zhipu_vision_mcp.server import analyze_video
        f = tmp_path / "small.mp4"
        f.write_bytes(b"\x00" * 1024)
        with patch("zhipu_vision_mcp.server.call_vision", return_value="ok"):
            result = analyze_video(str(f), "test")
            assert result == "ok"

    def test_video_url_skips_size_check(self):
        from zhipu_vision_mcp.server import analyze_video
        with patch("zhipu_vision_mcp.server.call_vision", return_value="ok"):
            result = analyze_video("https://example.com/video.mp4", "test")
            assert result == "ok"


class TestCallVision:
    def test_api_error_handling(self):
        from zhipu_vision_mcp.server import call_vision
        with patch("zhipu_vision_mcp.server.get_client") as mock_client:
            mock_client.return_value.chat.completions.create.side_effect = Exception("API timeout")
            with pytest.raises(ValueError, match="ZhipuAI API error"):
                call_vision("glm-4.6v", [{"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}], "test")

    def test_thinking_disabled(self):
        from zhipu_vision_mcp.server import call_vision
        with patch("zhipu_vision_mcp.server.get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.choices = [MagicMock()]
            mock_resp.choices[0].message.content = "result"
            mock_resp.choices[0].message.reasoning_content = None
            mock_client.return_value.chat.completions.create.return_value = mock_resp
            call_vision("glm-4.6v", [{"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}], "test", thinking=False)
            call_kwargs = mock_client.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["thinking"] == {"type": "disabled"}

    def test_thinking_enabled(self):
        from zhipu_vision_mcp.server import call_vision
        with patch("zhipu_vision_mcp.server.get_client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.choices = [MagicMock()]
            mock_resp.choices[0].message.content = "result"
            mock_resp.choices[0].message.reasoning_content = None
            mock_client.return_value.chat.completions.create.return_value = mock_resp
            call_vision("glm-4.6v", [{"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}], "test", thinking=True)
            call_kwargs = mock_client.return_value.chat.completions.create.call_args[1]
            assert call_kwargs["thinking"] == {"type": "enabled"}
