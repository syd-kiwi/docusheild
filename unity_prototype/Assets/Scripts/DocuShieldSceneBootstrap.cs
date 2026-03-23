using UnityEngine;

public class DocuShieldSceneBootstrap : MonoBehaviour
{
    private readonly Vector3 deskScale = new Vector3(3.2f, 0.15f, 1.4f);
    private readonly Vector3 shelfScale = new Vector3(0.9f, 2.2f, 0.4f);
    private readonly Vector3 whiteboardScale = new Vector3(2.8f, 1.4f, 0.06f);

    void Start()
    {
        CreateRoom();
        CreateDesk();
        CreateShelf();
        CreateWhiteboard();
        CreateSensitiveArtifact("Document", new Vector3(-0.9f, 0.83f, 0.1f), new Vector3(0.45f, 0.02f, 0.32f), new Color(1f, 0.99f, 0.88f));
        CreateSensitiveArtifact("Envelope", new Vector3(0.1f, 0.84f, 0.15f), new Vector3(0.50f, 0.02f, 0.22f), new Color(1f, 0.95f, 0.88f));
        CreateSensitiveArtifact("Notebook", new Vector3(0.9f, 0.86f, -0.1f), new Vector3(0.42f, 0.05f, 0.32f), new Color(0.88f, 0.94f, 1f));
    }

    private void CreateRoom()
    {
        var floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "Floor";
        floor.transform.localScale = new Vector3(1.8f, 1f, 1.2f);
        floor.GetComponent<Renderer>().material.color = new Color(0.93f, 0.95f, 0.98f);

        var backWall = GameObject.CreatePrimitive(PrimitiveType.Cube);
        backWall.name = "BackWall";
        backWall.transform.position = new Vector3(0f, 1.5f, 3.2f);
        backWall.transform.localScale = new Vector3(8f, 3.4f, 0.1f);
        backWall.GetComponent<Renderer>().material.color = new Color(0.82f, 0.87f, 0.92f);
    }

    private void CreateDesk()
    {
        var desk = GameObject.CreatePrimitive(PrimitiveType.Cube);
        desk.name = "Desk";
        desk.transform.position = new Vector3(0f, 0.75f, 0f);
        desk.transform.localScale = deskScale;
        desk.GetComponent<Renderer>().material.color = new Color(0.54f, 0.37f, 0.24f);
    }

    private void CreateShelf()
    {
        var shelf = GameObject.CreatePrimitive(PrimitiveType.Cube);
        shelf.name = "Shelf";
        shelf.transform.position = new Vector3(-2.5f, 1.1f, 1.6f);
        shelf.transform.localScale = shelfScale;
        shelf.GetComponent<Renderer>().material.color = new Color(0.42f, 0.30f, 0.24f);
    }

    private void CreateWhiteboard()
    {
        var whiteboard = GameObject.CreatePrimitive(PrimitiveType.Cube);
        whiteboard.name = "Whiteboard";
        whiteboard.transform.position = new Vector3(0f, 1.8f, 3.05f);
        whiteboard.transform.localScale = whiteboardScale;
        whiteboard.GetComponent<Renderer>().material.color = Color.white;
    }

    private void CreateSensitiveArtifact(string label, Vector3 position, Vector3 scale, Color color)
    {
        var artifact = GameObject.CreatePrimitive(PrimitiveType.Cube);
        artifact.name = label;
        artifact.transform.position = position;
        artifact.transform.localScale = scale;
        artifact.GetComponent<Renderer>().material.color = color;
    }
}
