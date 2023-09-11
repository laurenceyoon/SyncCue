// OSCServer.cs는 실제 유니티에서 사용될 C# 스크립트입니당 

using UnityEngine;
using System.Collections;
using System.Threading; // Sleep을 위해 사용

public class OSCServer : MonoBehaviour
{
    public OSC osc;

    [SerializeField]
    private GameObject cube;
    private Renderer cubeRenderer;
    private Color newCubeColor;
    private float R, G, B;

    void Start(){
        cubeRenderer = cube.GetComponent<Renderer>();
        osc.SetAddressHandler("/start", OnStart);
        osc.SetAddressHandler("/detect", OnDetect);
    }

    // Update is called once per frame
    void Update(){

    }

    void OnStart(OscMessage msg){
        Debug.LogFormat("Received: {0}", msg);
        int IsStart = msg.GetInt(0); // 1이면 Start
        newCubeColor = new Color(1f, 0f, 0f, 1f); // Red
        cubeRenderer.material.SetColor("_Color", newCubeColor);
    }

    void OnDetect(OscMessage msg){
        Debug.LogFormat("Received: {0}", msg);
        int gap = (int)(1000 / 30 * msg.GetInt(0)); // 30fps (gap: milliseconds)
        newCubeColor = new Color(1, 0.92f, 0.016f, 1); // Yellow
        cubeRenderer.material.SetColor("_Color", newCubeColor);
        Thread.Sleep(gap); // 잠시 대기 후
        newCubeColor = new Color(0, 1, 0, 1); // Green (MIDI ONSET)
        cubeRenderer.material.SetColor("_Color", newCubeColor);
    }
}