using System.Collections.Generic;
using UnityEngine;

public class DocuShieldOverlayDemo : MonoBehaviour
{
    public float riskScore = 0.82f;
    private DocuShieldDetectorContract detectorContract;
    private GUIStyle headerStyle;
    private GUIStyle labelStyle;

    void Start()
    {
        detectorContract = GetComponent<DocuShieldDetectorContract>();
        headerStyle = new GUIStyle
        {
            fontSize = 24,
            fontStyle = FontStyle.Bold,
            normal = { textColor = Color.white }
        };
        labelStyle = new GUIStyle
        {
            fontSize = 16,
            normal = { textColor = Color.white }
        };
    }

    void OnGUI()
    {
        var detections = detectorContract != null ? detectorContract.GetMockDetections() : new List<DocuShieldDetectorContract.DetectionResult>();

        GUI.color = new Color(0.8f, 0.15f, 0.15f, 0.92f);
        GUI.Box(new Rect(20f, 20f, 360f, 70f), GUIContent.none);
        GUI.Label(new Rect(35f, 35f, 320f, 30f), "DocuShield Alert", headerStyle);
        GUI.Label(new Rect(35f, 58f, 320f, 20f), $"Risk score: {riskScore:F2} | Blur sensitive artifacts", labelStyle);

        foreach (var detection in detections)
        {
            GUI.color = new Color(1f, 0.24f, 0.24f, 0.15f);
            GUI.Box(detection.boundingBox, GUIContent.none);
            GUI.color = new Color(1f, 0.24f, 0.24f, 0.95f);
            GUI.Box(new Rect(detection.boundingBox.x, detection.boundingBox.y - 24f, 220f, 24f), GUIContent.none);
            GUI.Label(new Rect(detection.boundingBox.x + 8f, detection.boundingBox.y - 22f, 210f, 20f),
                $"{detection.classLabel} ({detection.confidence:F2})", labelStyle);
        }
    }
}
