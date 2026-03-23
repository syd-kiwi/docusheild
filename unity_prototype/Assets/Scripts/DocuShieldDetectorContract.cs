using System.Collections.Generic;
using UnityEngine;

public class DocuShieldDetectorContract : MonoBehaviour
{
    [System.Serializable]
    public struct DetectionResult
    {
        public string classLabel;
        public Rect boundingBox;
        public float confidence;
    }

    [TextArea(4, 8)]
    public string pipelineDescription =
        "MainCamera -> RenderTexture -> Texture2D.ReadPixels -> YOLO ONNX tensor -> bounding boxes + labels + confidence -> risk score";

    public List<DetectionResult> GetMockDetections()
    {
        return new List<DetectionResult>
        {
            new DetectionResult { classLabel = "document", confidence = 0.94f, boundingBox = new Rect(180f, 260f, 320f, 160f) },
            new DetectionResult { classLabel = "envelope", confidence = 0.88f, boundingBox = new Rect(620f, 280f, 220f, 120f) },
            new DetectionResult { classLabel = "notebook", confidence = 0.86f, boundingBox = new Rect(900f, 300f, 250f, 170f) },
            new DetectionResult { classLabel = "whiteboard", confidence = 0.91f, boundingBox = new Rect(260f, 40f, 450f, 230f) },
        };
    }
}
