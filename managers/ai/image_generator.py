"""
AI Image Generator - Genera immagini usando DALL-E (OpenAI)

Features:
- DALL-E 3 (alta qualità)
- DALL-E 2 (economico)
- Download e salvataggio automatico
- Error handling e retry logic
"""
from typing import Optional, List, Dict
import requests
import base64
from pathlib import Path
import time
from dataclasses import dataclass
from utils.logger import logger


@dataclass
class ImageGenerationResult:
    """Risultato generazione immagine"""
    success: bool
    image_path: Optional[str] = None
    url: Optional[str] = None
    revised_prompt: Optional[str] = None  # DALL-E 3 rivede il prompt
    error: Optional[str] = None
    cost_estimate: float = 0.0


class AIImageGenerator:
    """
    Genera immagini usando DALL-E (OpenAI)

    Supporta:
    - DALL-E 3: Alta qualità, photorealistic
    - DALL-E 2: Più economico, buona qualità
    """

    # Pricing (USD per image)
    PRICING = {
        'dall-e-3': {
            'standard-1024x1024': 0.040,
            'standard-1024x1792': 0.080,
            'standard-1792x1024': 0.080,
            'hd-1024x1024': 0.080,
            'hd-1024x1792': 0.120,
            'hd-1792x1024': 0.120,
        },
        'dall-e-2': {
            '1024x1024': 0.020,
            '512x512': 0.018,
            '256x256': 0.016,
        }
    }

    def __init__(self, api_key: str):
        """
        Initialize image generator

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        self.api_base = "https://api.openai.com/v1/images/generations"

    def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        save_directory: Optional[Path] = None,
        filename_prefix: str = "generated"
    ) -> List[ImageGenerationResult]:
        """
        Genera immagine/i da prompt

        Args:
            prompt: Descrizione immagine
            model: "dall-e-3" o "dall-e-2"
            size: Dimensioni (es. "1024x1024", "1024x1792")
            quality: "standard" o "hd" (solo DALL-E 3)
            n: Numero immagini (DALL-E 2: 1-10, DALL-E 3: solo 1)
            save_directory: Directory dove salvare
            filename_prefix: Prefisso nome file

        Returns:
            List[ImageGenerationResult]: Risultati generazione
        """
        logger.info(f"Generating image with {model}")
        logger.info(f"[FULL_PROMPT] {prompt}")

        # Validate parameters
        if model == "dall-e-3" and n > 1:
            logger.warning("DALL-E 3 supports only n=1, setting n=1")
            n = 1

        if model == "dall-e-2" and quality == "hd":
            logger.warning("DALL-E 2 doesn't support HD quality, using standard")
            quality = "standard"

        # Build request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
        }

        # DALL-E 3 specific params
        if model == "dall-e-3":
            payload["quality"] = quality
            payload["style"] = "vivid"  # or "natural"

        # Calculate cost estimate
        cost_key = f"{quality}-{size}" if model == "dall-e-3" else size
        cost_per_image = self.PRICING.get(model, {}).get(cost_key, 0.0)
        total_cost = cost_per_image * n

        logger.info(f"Estimated cost: ${total_cost:.3f} (${cost_per_image:.3f} x {n})")

        try:
            # Make API request
            response = requests.post(
                self.api_base,
                headers=headers,
                json=payload,
                timeout=60  # DALL-E can take time
            )

            response.raise_for_status()
            data = response.json()

            results = []

            # Process each generated image
            for i, image_data in enumerate(data.get('data', [])):
                url = image_data.get('url')
                revised_prompt = image_data.get('revised_prompt')  # DALL-E 3 only

                if not url:
                    results.append(ImageGenerationResult(
                        success=False,
                        error="No URL in response",
                        cost_estimate=cost_per_image
                    ))
                    continue

                # Download and save image
                image_path = None
                if save_directory:
                    image_path = self._download_image(
                        url,
                        save_directory,
                        f"{filename_prefix}_{i+1}"
                    )

                results.append(ImageGenerationResult(
                    success=True,
                    image_path=image_path,
                    url=url,
                    revised_prompt=revised_prompt,
                    cost_estimate=cost_per_image
                ))

                logger.info(f"Image {i+1}/{n} generated successfully")
                if revised_prompt:
                    logger.debug(f"Revised prompt: {revised_prompt[:100]}...")

            return results

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)

            # Parse OpenAI error
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
            except:
                pass

            logger.error(f"Image generation failed: {error_msg}")

            return [ImageGenerationResult(
                success=False,
                error=error_msg,
                cost_estimate=0.0
            )]

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return [ImageGenerationResult(
                success=False,
                error=str(e),
                cost_estimate=0.0
            )]

    def _download_image(
        self,
        url: str,
        directory: Path,
        filename: str
    ) -> Optional[str]:
        """
        Scarica immagine da URL

        Args:
            url: URL immagine
            directory: Directory destinazione
            filename: Nome file (senza estensione)

        Returns:
            str: Path completo file salvato, o None se errore
        """
        try:
            # Create directory if needed
            directory.mkdir(parents=True, exist_ok=True)

            # Download image
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Save with timestamp to avoid collisions
            timestamp = int(time.time())
            filepath = directory / f"{filename}_{timestamp}.png"

            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.info(f"Image saved to: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None

    def estimate_cost(
        self,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1
    ) -> float:
        """
        Stima costo generazione

        Args:
            model: "dall-e-3" o "dall-e-2"
            size: Dimensioni
            quality: "standard" o "hd"
            n: Numero immagini

        Returns:
            float: Costo stimato in USD
        """
        cost_key = f"{quality}-{size}" if model == "dall-e-3" else size
        cost_per_image = self.PRICING.get(model, {}).get(cost_key, 0.0)
        return cost_per_image * n

    @staticmethod
    def get_available_sizes(model: str) -> List[str]:
        """
        Ottieni dimensioni disponibili per modello

        Args:
            model: "dall-e-3" o "dall-e-2"

        Returns:
            List[str]: Lista dimensioni disponibili
        """
        if model == "dall-e-3":
            return ["1024x1024", "1024x1792", "1792x1024"]
        else:  # dall-e-2
            return ["1024x1024", "512x512", "256x256"]

    @staticmethod
    def get_available_qualities(model: str) -> List[str]:
        """
        Ottieni qualità disponibili per modello

        Args:
            model: "dall-e-3" o "dall-e-2"

        Returns:
            List[str]: Lista qualità disponibili
        """
        if model == "dall-e-3":
            return ["standard", "hd"]
        else:  # dall-e-2
            return ["standard"]
