import { GoogleGenAI } from "@google/genai";

// Initialize the client
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

/**
 * Generates an image based on a text prompt using Gemini 2.5 Flash Image model.
 * @param prompt The user's description of the image.
 * @param aspectRatio The desired aspect ratio (e.g., "1:1", "9:16").
 * @returns A base64 data URL of the generated image.
 */
export const generateImageWithGemini = async (
  prompt: string, 
  aspectRatio: string = "1:1"
): Promise<string> => {
  try {
    const modelId = 'gemini-2.5-flash-image';
    
    const response = await ai.models.generateContent({
      model: modelId,
      contents: {
        parts: [{ text: prompt }],
      },
      config: {
        imageConfig: {
          aspectRatio: aspectRatio,
        },
      },
    });

    const parts = response.candidates?.[0]?.content?.parts;
    if (!parts) {
      throw new Error("No content generated");
    }

    for (const part of parts) {
      if (part.inlineData) {
        const base64EncodeString = part.inlineData.data;
        const mimeType = part.inlineData.mimeType || 'image/png';
        return `data:${mimeType};base64,${base64EncodeString}`;
      }
    }

    const textPart = parts.find(p => p.text);
    if (textPart) {
      console.warn("Model returned text instead of image:", textPart.text);
      throw new Error(textPart.text || "Model did not return an image.");
    }

    throw new Error("Unexpected response format from Gemini.");

  } catch (error) {
    console.error("Gemini Image Generation Error:", error);
    throw error;
  }
};