"""
VisionService for image analysis using BLIP-2 (open source, local, zero cost).

Local alternative to Gemini Vision.
Uses Salesforce BLIP-2 for image captioning and visual question answering.
"""

import logging
import os
import tempfile

import httpx
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

logger = logging.getLogger(__name__)


class VisionService:
    """
    Image analysis service using BLIP-2 (local, no external API cost).

    Model: Salesforce/blip-image-captioning-base
    - Open source (BSD-3 License)
    - Runs locally (CPU or GPU)
    - ~990MB initial download
    - Zero API cost
    - Good quality for captioning

    Features:
    - Generate automatic image descriptions
    - Visual Question Answering (VQA)
    - Contextual analysis for health/weight loss
    """

    def __init__(self):
        """Initialize BLIP-2 model (lazy loading)."""
        self.processor = None
        self.model = None
        self.model_name = "Salesforce/blip-image-captioning-base"

    def _load_model(self):
        """Load BLIP-2 model on demand."""
        if self.model is None:
            logger.info("Loading BLIP-2 model: %s (~990MB)...", self.model_name)
            try:
                self.processor = BlipProcessor.from_pretrained(self.model_name)
                self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
                logger.info("[SUCCESS] BLIP-2 model loaded successfully")
            except Exception as e:  # noqa: BLE001 (blind exception)
                logger.error("[ERROR] Failed to load BLIP-2: %s", e)
                raise

    async def analyze_image(
        self, image_url: str, context: str = "medical", questions: list[str] | None = None
    ) -> dict[str, str]:
        """
        Analyze image and generate a detailed description.

        Args:
            image_url: Image URL
            context: Analysis context (medical, fitness, food, etc.)
            questions: Specific questions for VQA

        Returns:
            Dict with:
            - caption: Main image description
            - detailed_description: Detailed analysis
            - tags: Relevant tags
            - answers: Answers for questions (if provided)
        """
        self._load_model()

        try:
            # 1. Download image
            logger.info("[INFO] Downloading image from: %s", image_url)
            image = await self._download_image(image_url)

            # 2. Generate basic caption
            caption = await self._generate_caption(image)
            logger.info("[SUCCESS] Caption generated: %s", caption)

            # 3. Generate detailed description with contextual questions
            detailed_description = await self._generate_detailed_description(image, caption, context)

            # 4. Extract tags from description
            tags = self._extract_tags(caption, detailed_description, context)

            # 5. Answer custom questions (VQA)
            answers = {}
            if questions:
                for question in questions:
                    answer = await self._answer_question(image, question)
                    answers[question] = answer

            return {"caption": caption, "detailed_description": detailed_description, "tags": tags, "answers": answers}

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Failed to analyze image: %s", e)
            raise

    async def _download_image(self, url: str) -> Image.Image:
        """Download image from URL."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name

            # Open with PIL
            image = Image.open(tmp_path).convert("RGB")

            # Clean up temporary file
            os.unlink(tmp_path)

            return image

    async def _generate_caption(self, image: Image.Image) -> str:
        """Generate a basic caption for the image."""
        # Process image
        inputs = self.processor(image, return_tensors="pt")

        # Gerar caption
        output = self.model.generate(**inputs, max_new_tokens=50)
        return self.processor.decode(output[0], skip_special_tokens=True)

    async def _generate_detailed_description(self, image: Image.Image, caption: str, context: str) -> str:
        """
        Generate a detailed description including contextual questions.

        For medical/weight loss context, ask questions like:
        - "What type of food is shown?"
        - "Is this a healthy meal?"
        - "What activities are visible?"
        """
        if context == "medical":
            questions = [
                "What is the main subject of this image?",
                "What details are visible?",
                "What colors and objects are present?",
            ]
        else:
            questions = ["What is shown in this image?", "What are the key details?"]

        descriptions = [caption]

        for question in questions:
            answer = await self._answer_question(image, question)
            descriptions.append(answer)

        return " ".join(descriptions)

    async def _answer_question(self, image: Image.Image, question: str) -> str:
        """Answer a question about the image (VQA)."""
        # BLIP supports conditional generation with a prompt
        prompt = f"Question: {question} Answer:"

        inputs = self.processor(image, text=prompt, return_tensors="pt")
        output = self.model.generate(**inputs, max_new_tokens=30)
        answer = self.processor.decode(output[0], skip_special_tokens=True)

        # Remove prompt from the answer
        return answer.replace(prompt, "").strip()

    def _extract_tags(self, caption: str, description: str, context: str) -> str:
        """Extract relevant tags from the description."""
        text = f"{caption} {description}".lower()

        # Base tags
        tags = ["imagem", "análise visual"]

        # Contextual keywords for health/weight loss
        health_keywords = {
            "food": "alimentação",
            "meal": "refeição",
            "plate": "prato",
            "salad": "salada",
            "fruit": "fruta",
            "vegetable": "vegetal",
            "exercise": "exercício",
            "workout": "treino",
            "gym": "academia",
            "running": "corrida",
            "walking": "caminhada",
            "person": "pessoa",
            "woman": "mulher",
            "man": "homem",
            "healthy": "saudável",
            "diet": "dieta",
            "nutrition": "nutrição",
        }

        for keyword, tag in health_keywords.items():
            if keyword in text:
                tags.append(tag)

        # Add context tag
        if context == "medical":
            tags.append("contexto médico")

        return ", ".join(tags[:10])  # Max 10 tags

    def analyze_image_sync(self, image_url: str, context: str = "medical") -> dict[str, str]:
        """
        Synchronous version of `analyze_image`.

        Useful for background jobs (RQ).
        """
        import asyncio

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.analyze_image(image_url, context))


# Singleton para reutilizar modelo carregado
_vision_service_instance: VisionService | None = None


def get_vision_service() -> VisionService:
    """Get singleton instance of `VisionService`."""
    global _vision_service_instance

    if _vision_service_instance is None:
        _vision_service_instance = VisionService()

    return _vision_service_instance
