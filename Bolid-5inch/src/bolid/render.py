"""Pictures of the model: VTK, off screen, flat-shaded with outlines, one light rig for every image."""

from dataclasses import dataclass
from pathlib import Path

from build123d import Part

PALETTE = {
    "carbon": (0.16, 0.17, 0.19),
    "aluminium": (0.72, 0.78, 0.84),
    "tpu": (0.86, 0.88, 0.90),
    "shell": (0.95, 0.95, 0.96),  # the body: clean gloss white
    "accent": (0.86, 0.06, 0.10),  # one racing red for what takes the hits
    "light": (1.00, 0.18, 0.15),
    "dark": (0.10, 0.10, 0.11),
    "pcb": (0.13, 0.40, 0.30),
    "motor": (0.42, 0.44, 0.48),
    "prop": (0.60, 0.80, 0.98),
    "battery": (0.30, 0.32, 0.38),
    "camera": (0.20, 0.20, 0.23),
    "clear": (0.75, 0.92, 1.00),
}
VIEWS = {
    "front_iso": ((1.0, 1.25, 0.75), (0, 0, 1), False),
    "rear_iso": ((0.9, -1.3, 0.7), (0, 0, 1), False),
    "low": ((0.6, 1.3, 0.25), (0, 0, 1), False),
    "under": ((0.9, -1.0, -0.8), (0, 0, 1), False),
    "top": ((0, 0, 1), (0, 1, 0), True),
    "side": ((1, 0, 0), (0, 0, 1), True),
    "tail": ((0.35, -1.0, 0.35), (0, 0, 1), False),
    "iso": ((1.0, -1.2, 0.9), (0, 0, 1), False),
}


@dataclass
class Item:
    part: Part
    color: str = "carbon"
    opacity: float = 1.0
    edges: bool = True


def _polydata(part: Part, tol: float):
    import vtk

    verts, tris = part.tessellate(tol, 0.2)
    pts = vtk.vtkPoints()
    for v in verts:
        pts.InsertNextPoint(v.X, v.Y, v.Z)
    cells = vtk.vtkCellArray()
    for a, b, c in tris:
        cells.InsertNextCell(3, (a, b, c))
    pd = vtk.vtkPolyData()
    pd.SetPoints(pts)
    pd.SetPolys(cells)
    clean = vtk.vtkCleanPolyData()
    clean.SetInputData(pd)
    clean.Update()
    return clean.GetOutput()


def render(items: list[Item], png: Path, view="front_iso", size=(1600, 1200), zoom=1.0, focus=None, tol=0.08) -> Path:
    import vtk

    vtk.vtkObject.GlobalWarningDisplayOff()
    ren = vtk.vtkRenderer()
    ren.SetBackground(1, 1, 1)
    bounds = None
    for it in items:
        pd = _polydata(it.part, tol)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(pd)
        normals.SetFeatureAngle(35)
        normals.Update()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(*PALETTE[it.color] if isinstance(it.color, str) else it.color)
        prop.SetOpacity(it.opacity)
        prop.SetAmbient(0.25)
        prop.SetDiffuse(0.75)
        prop.SetSpecular(0.35 if it.color in ("carbon", "aluminium", "clear", "shell", "accent") else 0.08)
        prop.SetSpecularPower(30)
        ren.AddActor(actor)
        if it.edges:
            fe = vtk.vtkFeatureEdges()
            fe.SetInputData(pd)
            fe.BoundaryEdgesOn()
            fe.FeatureEdgesOn()
            fe.SetFeatureAngle(35)
            fe.ManifoldEdgesOff()
            fe.NonManifoldEdgesOff()
            em = vtk.vtkPolyDataMapper()
            em.SetInputConnection(fe.GetOutputPort())
            em.ScalarVisibilityOff()
            ea = vtk.vtkActor()
            ea.SetMapper(em)
            ea.GetProperty().SetColor(0.9, 0.93, 0.96) if it.color == "carbon" else ea.GetProperty().SetColor(
                0.05, 0.05, 0.06
            )
            ea.GetProperty().SetLineWidth(1.0)
            ea.GetProperty().SetOpacity(0.6 * it.opacity)
            ren.AddActor(ea)
        if focus is None or any(it.part is f for f in focus):
            b = pd.GetBounds()
            bounds = (
                b
                if bounds is None
                else [
                    min(bounds[0], b[0]),
                    max(bounds[1], b[1]),
                    min(bounds[2], b[2]),
                    max(bounds[3], b[3]),
                    min(bounds[4], b[4]),
                    max(bounds[5], b[5]),
                ]
            )
    d, up, parallel = VIEWS[view] if isinstance(view, str) else view
    cam = ren.GetActiveCamera()
    c = [(bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2, (bounds[4] + bounds[5]) / 2]
    cam.SetFocalPoint(*c)
    cam.SetPosition(c[0] + d[0] * 1000, c[1] + d[1] * 1000, c[2] + d[2] * 1000)
    cam.SetViewUp(*up)
    cam.SetParallelProjection(parallel)
    ren.ResetCamera(bounds)
    cam.Zoom(zoom * 1.25)
    ren.ResetCameraClippingRange()
    lights = vtk.vtkLightKit()
    lights.SetKeyLightIntensity(1.0)
    lights.SetKeyToFillRatio(2.5)
    lights.SetKeyLightWarmth(0.45)  # cool key light: the frame should look cold and technical
    lights.AddLightsToRenderer(ren)
    if any(i.opacity < 1 for i in items):
        ren.SetUseDepthPeeling(1)
        ren.SetMaximumNumberOfPeels(8)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetMultiSamples(0)  # software GL off screen has no multisampled buffer: render large and shrink instead
    win.AddRenderer(ren)
    win.SetSize(size[0] * 2, size[1] * 2)
    win.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.SetInputBufferTypeToRGB()
    grab.ReadFrontBufferOff()  # off screen, the picture is in the back buffer
    grab.Update()
    out = vtk.vtkPNGWriter()
    png.parent.mkdir(parents=True, exist_ok=True)
    out.SetFileName(str(png))
    out.SetInputConnection(grab.GetOutputPort())
    out.Write()
    from PIL import Image

    with Image.open(png) as im:
        im.resize(size, Image.LANCZOS).save(png, optimize=True)
    return png
