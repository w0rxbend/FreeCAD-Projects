"""Shaded PNG previews with VTK (optional dependency: `uv sync --extra render`).

VTK needs an OpenGL context. On a headless machine run under a virtual display:
`xvfb-run -a uv run zhalo render` (the CLI re-executes itself that way when DISPLAY is unset).
"""

from dataclasses import dataclass
from pathlib import Path

from build123d import Part

RGB = tuple[float, float, float]

COLORS: dict[str, RGB] = {
    "carbon": (0.23, 0.24, 0.27),
    "aluminium": (0.80, 0.62, 0.16),
    "tpu": (0.97, 0.76, 0.10),
    "tpu_dark": (0.20, 0.21, 0.23),
    "pcb": (0.10, 0.42, 0.30),
    "motor": (0.45, 0.47, 0.52),
    "prop": (0.55, 0.75, 0.95),
    "battery": (0.35, 0.38, 0.45),
    "camera": (0.25, 0.25, 0.28),
    "highlight": (0.90, 0.22, 0.16),
}

# name -> (direction from the target to the camera, view-up, parallel projection)
VIEWS = {
    "iso": ((1.0, -1.25, 0.85), (0, 0, 1), False),
    "iso_rear": ((-1.0, 1.25, 0.8), (0, 0, 1), False),
    "iso_low": ((1.0, -1.0, 0.35), (0, 0, 1), False),
    "under": ((0.8, -1.0, -0.9), (0, 0, 1), False),
    "top": ((0, 0, 1), (0, 1, 0), True),
    "bottom": ((0, 0, -1), (0, 1, 0), True),
    "side": ((1, 0, 0), (0, 0, 1), True),
    "front": ((0, 1, 0), (0, 0, 1), True),
    "rear": ((0, -1, 0), (0, 0, 1), True),
}


@dataclass
class Item:
    part: Part
    color: RGB | str = "carbon"
    opacity: float = 1.0
    edges: bool = True


def _polydata(part: Part, tolerance: float):
    import vtk

    verts, tris = part.tessellate(tolerance, 0.25)
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(len(verts))
    for i, v in enumerate(verts):
        points.SetPoint(i, v.X, v.Y, v.Z)
    cells = vtk.vtkCellArray()
    for a, b, c in tris:
        cells.InsertNextCell(3, (a, b, c))
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    clean = vtk.vtkCleanPolyData()  # faces are meshed one by one: weld them so edges can be found
    clean.SetInputData(poly)
    clean.SetTolerance(1e-6)
    clean.Update()
    return clean.GetOutput()


def render(
    items: list[Item],
    png: Path,
    view: str | tuple = "iso",
    size: tuple[int, int] = (1600, 1200),
    zoom: float = 1.0,
    tolerance: float = 0.05,
    focus: list[Part] | None = None,
) -> Path:
    """Render the items to a PNG. `focus` (default: everything) is what the camera frames."""
    import vtk

    vtk.vtkObject.GlobalWarningDisplayOff()
    ren = vtk.vtkRenderer()
    ren.SetBackground(1.0, 1.0, 1.0)
    ren.SetBackground2(0.86, 0.89, 0.93)
    ren.GradientBackgroundOn()
    for item in items:
        rgb = COLORS[item.color] if isinstance(item.color, str) else item.color
        poly = _polydata(item.part, tolerance)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(poly)
        normals.SetFeatureAngle(32.0)
        normals.SplittingOn()
        normals.ConsistencyOn()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(*rgb)
        prop.SetOpacity(item.opacity)
        prop.SetAmbient(0.28)
        prop.SetDiffuse(0.72)
        prop.SetSpecular(0.25)
        prop.SetSpecularPower(28)
        ren.AddActor(actor)
        if item.edges and item.opacity > 0.5:
            feat = vtk.vtkFeatureEdges()
            feat.SetInputData(poly)
            feat.SetFeatureAngle(32.0)
            feat.BoundaryEdgesOff()
            feat.NonManifoldEdgesOff()
            feat.ManifoldEdgesOff()
            feat.FeatureEdgesOn()
            feat.ColoringOff()
            emap = vtk.vtkPolyDataMapper()
            emap.SetInputConnection(feat.GetOutputPort())
            emap.SetResolveCoincidentTopologyToPolygonOffset()
            eact = vtk.vtkActor()
            eact.SetMapper(emap)
            dark = sum(rgb) / 3 < 0.35
            eact.GetProperty().SetColor(*((0.70, 0.72, 0.76) if dark else (0.18, 0.16, 0.10)))
            eact.GetProperty().SetLineWidth(2.0)
            eact.GetProperty().LightingOff()
            ren.AddActor(eact)

    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetMultiSamples(0)
    scale = 2  # supersample, then shrink: smoother than FXAA on thin CAD edges
    win.SetSize(size[0] * scale, size[1] * scale)
    win.AddRenderer(ren)

    direction, up, parallel = VIEWS[view] if isinstance(view, str) else view
    targets = focus if focus else [i.part for i in items]
    lo = [min(p.bounding_box().min.to_tuple()[k] for p in targets) for k in range(3)]
    hi = [max(p.bounding_box().max.to_tuple()[k] for p in targets) for k in range(3)]
    center = [(a + b) / 2 for a, b in zip(lo, hi, strict=True)]
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(*center)
    cam.SetPosition(*(c + d * 1000 for c, d in zip(center, direction, strict=True)))
    cam.SetViewUp(*up)
    cam.SetParallelProjection(parallel)
    cam.SetViewAngle(22)
    ren.ResetCamera(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
    cam.Zoom(zoom * (1.0 if parallel else 1.25))
    ren.ResetCameraClippingRange()

    light = vtk.vtkLight()
    light.SetLightTypeToCameraLight()
    light.SetPosition(-0.6, 0.9, 1.0)
    light.SetIntensity(0.85)
    ren.AddLight(light)
    fill = vtk.vtkLight()
    fill.SetLightTypeToCameraLight()
    fill.SetPosition(0.8, -0.4, 0.6)
    fill.SetIntensity(0.35)
    ren.AddLight(fill)
    try:
        ren.UseSSAOOn()
        ren.SetSSAORadius(8.0)
        ren.SetSSAOBias(0.5)
        ren.SetSSAOKernelSize(128)
        ren.SSAOBlurOn()
    except AttributeError:
        pass
    if any(i.opacity < 1 for i in items):
        ren.SetUseDepthPeeling(1)
        ren.SetMaximumNumberOfPeels(8)
        ren.SetOcclusionRatio(0.0)
        win.SetAlphaBitPlanes(1)

    win.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.SetInputBufferTypeToRGB()
    grab.ReadFrontBufferOff()
    grab.Update()
    png.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(png))
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()
    from PIL import Image

    with Image.open(png) as im:
        im.resize(size, Image.LANCZOS).save(png, optimize=True)
    return png
