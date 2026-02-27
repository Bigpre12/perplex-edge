import html2canvas from 'html2canvas';

/**
 * Captures a DOM element and triggers a high-resolution PNG download.
 * @param elementId The ID of the element to capture
 * @param fileName The name of the resulting file
 * @param scale The DPI scale (2-3 recommended for high-DPI social assets)
 */
export const exportComponentAsImage = async (
    elementId: string,
    fileName: string = 'perplex-edge-sharp.png',
    scale: number = 2
) => {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with id ${elementId} not found.`);
        return;
    }

    try {
        const canvas = await html2canvas(element, {
            scale: scale,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#050a08', // Match the card background
            logging: false,
        });

        // Convert to data URL and trigger download
        const image = canvas.toDataURL('image/png', 1.0);
        const link = document.createElement('a');
        link.download = fileName;
        link.href = image;
        link.click();

    } catch (err) {
        console.error('Error exporting image:', err);
        throw err;
    }
};
