# -*- coding: utf-8 -*-
"""
Classes and functions to deal with the visualisation of the AmpObjects. These
include wrappers for vtk and Qt
Copyright: Joshua Steer 2020, Joshua.Steer@soton.ac.uk 
"""

import numpy as np
import vtk
from vtk.util import numpy_support
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
vtk.vtkObject.GlobalWarningDisplayOff()


class vtkRenWin(vtk.vtkRenderWindow):
    r"""
    This class inherits from the vtkRenderWindow and wraps extra functions on
    top 
    
    This window can be either be used on it's own, or embedded within a 
    Qt Window

    """
    def __init__(self):
        super(vtkRenWin, self).__init__()
        self.rens = [vtk.vtkRenderer(),]
#        self.cams = [vtk.vtkCamera(),]
        self.axes = []
        self.AddRenderer(self.rens[0])
#        self.setView()
        self.scalar_bar = None
#        self.cams.append(vtk.vtkCamera())
#        self.setView()
#        self.rens.append(vtkRender())
#        self.rens[0].SetBackground(0.1, 0.2, 0.4)
#        self.rens[0].SetBackground(1.0,1.0,1.0)
        #self.rens[0].SetActiveCamera(self.cams[0])
#        self.axes.append(vtk.vtkCubeAxesActor())
        self.markers = []
        self.labels = []
        self.triad = None

        
    def renderActors(self, actors, viewport=0, zoom=1.0):
        r"""
        Given a list of ampActors, this function removes those which are not in 
        the new list, and adds in the new ones 
        
        Parameters
        ----------
        actors: list of ampActors
            A list of actors to be displayed in the render window
        viewport: int, default 0
            The viewport index to render the actor within
        zoom: float, default 1.0
            The zoom magnitude of the camera
        
        """
        for actor in self.rens[viewport].GetActors():
            self.rens[viewport].RemoveActor(actor)
        for actor in actors:
            self.rens[viewport].AddActor(actor)
            if hasattr(actor, 'pActors'):
                for p in actor.pActors:
                    self.rens[viewport].AddActor(p)
            if hasattr(actor, 'lActors'):
                for l in actor.lActors:
                    self.rens[viewport].AddActor(l)
        self.rens[viewport].ResetCamera()
        self.rens[viewport].GetActiveCamera().Zoom(zoom)
        self.Render()

    def setScalarBar(self, actor, viewport=0, title=''):
        r"""
        Set the scalar bar within the window based upon a look-up table defined
        within an actor
        
        Parameters
        ---------
        actor: ampActor
            The actor from which the lut is read from, the actor must have the
            attribute actor.lut
        viewport: int, default 0
            The viewport index to render the scalar bar within 
        title: str
            The accompanying title for the scalar bar
        
        Returns
        -------
        scalar_bar
            A vtkScalarBarActor attribute to the vtkRenWin
        
        """
        if self.scalar_bar is not None:
            self.rens[0].RemoveActor(self.scalar_bar)
        self.scalar_bar = vtk.vtkScalarBarActor()
#        self.scalar_bar.AnnotationTextScalingOff()
#        self.scalar_bar.SetTitle('Interfacial Pressure, kPa')
        self.scalar_bar.SetLookupTable(actor.lut)
        self.scalar_bar.UnconstrainedFontSizeOn()
        self.scalar_bar.SetOrientationToVertical()
        self.scalar_bar.SetPosition(0.8, 0.15)
        self.scalar_bar.SetPosition2(0.1, 0.7)
        self.scalar_bar.SetLabelFormat('%-#3.1f')
        self.scalar_bar.GetLabelTextProperty().SetFontFamilyToArial()
        self.scalar_bar.GetLabelTextProperty().BoldOff()
        self.scalar_bar.GetLabelTextProperty().ShadowOff()
        self.scalar_bar.GetLabelTextProperty().SetColor(0, 0, 0)
        self.scalar_bar.GetLabelTextProperty().SetFontSize(18)
        self.scalar_bar.GetLabelTextProperty().ItalicOff()
        self.scalar_bar.SetTitle(title)
        self.scalar_bar.GetTitleTextProperty().SetFontFamilyToArial()
        self.scalar_bar.GetTitleTextProperty().BoldOff()
        self.scalar_bar.GetTitleTextProperty().ShadowOff()
        self.scalar_bar.GetTitleTextProperty().SetColor(0, 0, 0)
        self.scalar_bar.GetTitleTextProperty().SetFontSize(20)
        self.scalar_bar.GetTitleTextProperty().ItalicOff()
        self.rens[viewport].AddActor(self.scalar_bar)

    def setView(self, view = [0, -1, 0], viewport=0):
        r"""
        Function to set the camera view within the specified viewport
        
        Parameters
        ----------
        view: array_like, default [0, -1, 0]
            The view of the vtk camera 
        viewport: int, default 0
            The index of the viewport to set the camera view
        
        """
        #self.cams[viewport].SetPosition(view[0], view[1], view[2])
        #self.cams[viewport].SetViewUp(-0.0, 1.0, 0.0)
        cam = self.rens[viewport].GetActiveCamera()
        cam.Elevation(-90)
    
    def setBackground(self, color=[0.1, 0.2, 0.4]):
        r"""
        Set the background colour of the renderer
        
        Parameters
        ----------
        color: array_like
            The RGB values as floats of the background colour between [0, 1]

        """
        for ren in self.rens:
            ren.SetBackground(color)
    
    def setProjection(self, perspective=False, viewport=0):
        r"""
        Set the projection of the camera to either parallel or perspective 
        
        Parameters
        ----------
        perspective: boolean, default False
            If true, then perspective will be used as the projection for the
            camera
        viewport: int, default 0
            The index of the viewport to set the projection of the camera in
        
        """
        cam = self.rens[viewport].GetActiveCamera()
        cam.SetParallelProjection(perspective)
        
            
    def addAxes(self, actors, viewport=0, color = [1.0, 1.0, 1.0], font=None):
        r"""
        Add 3D axes to the vtk window 
        
        Parameters
        ----------
        actors: list
            List of ampActors, this is used to determine the necessary limits
            of the axes
        viewport: int, default 0
            The index of the viewport add the axes into
        color: array_like
            The RGB values as floats of the axes line and text colour
            between [0, 1]
        """
        self.axes = vtk.vtkCubeAxesActor()
        lim = []
        ax = self.axes
        for actor in actors:
            lim.append(actor.GetBounds())
        if lim:
            lim = np.array(lim) * 1.2
            ax.SetBounds(tuple(lim.max(axis=0)))
        ax.SetCamera(self.rens[viewport].GetActiveCamera())
        ax.SetFlyModeToClosestTriad()
        for axes in range(3):
            ax.GetTitleTextProperty(axes).SetColor(color)
            ax.GetLabelTextProperty(axes).SetColor(color)
            ax.GetTitleTextProperty(axes).SetFontFamilyToCourier()
            ax.GetLabelTextProperty(axes).SetFontFamilyToCourier()
        ax.GetXAxesLinesProperty().SetColor(color)
        ax.GetYAxesLinesProperty().SetColor(color)
        ax.GetZAxesLinesProperty().SetColor(color)
        ax.XAxisMinorTickVisibilityOff()
        ax.YAxisMinorTickVisibilityOff()
        ax.ZAxisMinorTickVisibilityOff()
        actors.append(ax)
        self.renderActors(actors)

    def addTriad(self, actors, viewport=0, color = [1.0, 1.0, 1.0], font=None):
        r"""
        Add 3D axes to the vtk window 
        
        Parameters
        ----------
        actors: list
            List of ampActors, this is used to determine the necessary limits
            of the axes
        viewport: int, default 0
            The index of the viewport add the axes into
        color: array_like
            The RGB values as floats of the axes line and text colour
            between [0, 1]
        """
        lim = []
        for actor in actors:
            lim.append(actor.GetBounds())
        if lim:
            lim = np.array(lim) * 1.1
            lim = lim.max(axis=0)
        else:
            lim = [0, 1, 0, 1, 0, 1]
        transform = vtk.vtkTransform()
        transform.Translate(lim[0], lim[2], lim[4])
        scale = (lim[5] - lim[4]) * 0.1
        transform.Scale(scale, scale, scale)
        if self.triad:
            self.rens[viewport].RemoveActor(self.triad)
        self.triad = vtk.vtkAxesActor()
        #  The axes are positioned with a user transform
        self.triad.SetUserTransform(transform)
        for ax in [self.triad.GetXAxisCaptionActor2D(), self.triad.GetYAxisCaptionActor2D(), self.triad.GetZAxisCaptionActor2D()]:
            ax.GetTextActor().GetTextProperty().SetFontFamilyToCourier()
            ax.GetTextActor().GetTextProperty().SetColor(0, 0, 0)
            ax.GetTextActor().GetTextProperty().ShadowOff()
            ax.GetTextActor().GetTextProperty().BoldOff()
            ax.GetTextActor().GetTextProperty().ItalicOff()
            ax.GetTextActor().GetTextProperty().SetFontSize(8)
        self.rens[viewport].AddActor(self.triad)
        self.Render()


    def setnumViewports(self, n):
        r"""
        Function to set multiple viewports within the vtkWindow

        Parameters
        ------------
        n: int
            number of viewports required
        
        """
        dif = n - len(self.rens)
        if dif == 0:
            return
        elif dif < 0:
            for ren in self.rens[n:]:
                self.RemoveRenderer(ren)
            self.rens = self.rens[:n]
        elif dif > 0:
            for i in range(dif):
                self.rens.append(vtk.vtkRenderer())
                self.axes.append(vtk.vtkCubeAxesActor())
                self.AddRenderer(self.rens[-1])
                if len(self.cams) < len(self.rens):
                    self.cams.append(vtk.vtkCamera())
                self.rens[-1].SetActiveCamera(self.cams[len(self.rens)-1])
        for i, ren in enumerate(self.rens):
            ren.SetViewport(float(i)/n, 0, float(i+1)/n, 1)
        self.setBackground()
        
    
    def getImage(self):
        r"""
        Return an array representation of the image 
        
        Returns
        -------
        im: ndarray
            The array representation of the image 
        
        """
        vtkRGB = vtk.vtkUnsignedCharArray()
        width, height = self.GetSize()
        self.GetPixelData(0, 0, width-1, height-1,
                          1, vtkRGB)
        vtkRGB.Squeeze()
        im =  np.flipud(np.resize(np.array(vtkRGB),
                                  [height, width, 3])) / 255.0
        return im
                                       
    def getScreenshot(self, fname, mag=10):
        r"""
        Generate a screenshot of the window and save to a png file
        
        Parameters
        ----------
        fname: str
            The file handle to save the image to 
        mag: int, default 10
            The magnificaiton of the image, this will scale the resolution of 
            the saved image by this face 
        
        """
        self.SetAlphaBitPlanes(1)
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self)
        w2if.SetScale(mag)
        w2if.SetInputBufferTypeToRGBA()
        w2if.Update()
        
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(fname)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

    def Pick_point(self, loc):
        """
        This receives coordinates in the GUI where user has picked, converts it
        to mesh coordinates using vtkCellPicker, and places a sphere at picked
        location as a visual aid. Also places a label at the point in the 
        render window.
        TO-DO: Add functionality so user can type the label in, rather than
        have it read 'Mid Patella' every time
        """
        
        x, y = loc
        renderer = self.rens[0]
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.01)
        picker.Pick(x, y, 0, renderer)
        points = picker.GetPickedPositions()
        numPoints = points.GetNumberOfPoints()
        #if no points selected, exits function
        if numPoints<1: return
        # Calls function to create a sphere at selected point
        pnt = points.GetPoint(0)
        self.mark(pnt[0], pnt[1], pnt[2])
        # Creating label at selected point
        label = vtk.vtkStringArray()
        label.SetName('label')
        label.InsertNextValue("   Mid Patella")
        lPoints = vtk.vtkPolyData()
        lPoints.SetPoints(points)
        lPoints.GetPointData().AddArray(label)
        
        hier = vtk.vtkPointSetToLabelHierarchy()
        hier.SetInputData(lPoints)
        hier.SetLabelArrayName('label')
        hier.GetTextProperty().SetColor(0,0,0)
        hier.GetTextProperty().SetFontSize(30)
        
        lMapper = vtk.vtkLabelPlacementMapper()
        lMapper.SetInputConnection(hier.GetOutputPort())
        lMapper.SetBackgroundColor(0.3,0.3,0.3)
        lMapper.SetBackgroundOpacity(0.8)
        lMapper.SetMargin(10)
        
        lActor = vtk.vtkActor2D()
        lActor.SetMapper(lMapper)
        self.labels.append(lActor) # keep track of all label actors
        
        self.rens[0].AddActor(lActor)
        self.Render()
        return pnt
        

    def mark(self, x,y,z):
        """
        mark the picked point with a sphere
        """
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(3)
        res = 20
        sphere.SetThetaResolution(res)
        sphere.SetPhiResolution(res)
        sphere.SetCenter(x,y,z)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        self.marker = vtk.vtkActor()
        self.marker.SetMapper(mapper)
        self.rens[0].AddActor(self.marker)
        self.marker.GetProperty().SetColor( (1,0,0) )
        self.markers.append(self.marker) #keep track of all marker actors
        self.Render()

    def delMarker(self):
        """
        removes the sphere marker and label from the renderer
        """
        for i in self.markers:
            self.rens[0].RemoveActor(i)
        for i in self.labels:
            self.rens[0].RemoveActor(i)
        self.markers = []
        self.labels = []


class qtVtkWindow(QVTKRenderWindowInteractor):
    r"""
    This provides the interface between Qt and the vtkRenWin
    """
    
    def __init__(self):
        super(qtVtkWindow, self).__init__(rw=vtkRenWin())
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.SetInteractorStyle(self.style)
        self.iren = self._RenderWindow.GetInteractor()
        self.iren.Initialize()        


class visMixin(object):
    r"""
    Set of visualisation methods that are contained within the AmpActor
    
    """

    def genIm(self, size=[512, 512], views=[[0, -1, 0]], 
              background=[1.0, 1.0, 1.0], projection=True,
              shading=True, mag=10, out='im', fh='test.tiff', 
              zoom=1.0, az = 0, el=0,crop=False, cam=None):
        r"""
        Creates a temporary off screen vtkRenWin which is then either returned
        as a numpy array or saved as a .png file
        
        Parameters
        ----------
        out: str: default 'im'
            If 'im' the the image will be returned as an array, if 'fh' the 
            image will be saved as .png image
        size: array_like, default [512, 512]
            The width and height of the vtkRenWin to create
        views: array_like, default [[0, -1, 0],]
            The camera view set for each viewport, the length of this also
            sets the number of viewports
        background: array_like, default [1, 1, 1]
            The RGB values as floats of the background colour between [0, 1]
        projection: boolean, default True
            If true, then perspective will be used as the projection for the
            camera
        shading: boolean, default True
            If true, shading will be used on the ampActor
        mag: int, default 10
            The magnification for saving the image
        fh: str
            The file handle used if out ='fh'
        
        Returns
        -------
        im: ndarray
            The array representation of the image if out = 'im'
        
        """
        if not hasattr(self, 'actor'):
            self.addActor()
        # Generate a renderer window
        win = vtkRenWin()
        win.OffScreenRenderingOn()
        # Set the number of viewports
        win.setnumViewports(len(views))
        # Set the background colour
        win.setBackground(background)
        # Set camera projection 
        win.setProjection(projection)
        win.SetSize(size[0], size[1])
        win.Modified()
        win.OffScreenRenderingOn()
        
        for i, view in enumerate(views):
#            win.addAxes([self.actor,], color=[0.0, 0.0, 0.0], viewport=i)
            win.setView(view, i)
#            win.setProjection(projection, viewport=i)
            win.renderActors([self.actor,], zoom=zoom)
        win.rens[0].GetActiveCamera().Azimuth(az)
        if cam is not None:
            win.rens[0].SetActiveCamera(cam)
        win.Render()
        if out == 'im':
            im = win.getImage()
            if crop is True:
                mask = np.all(im == 1, axis=2)
                mask = ~np.all(mask, axis=1)
                im = im[mask, :, :]
                mask = np.all(im == 1, axis=2)
                mask = ~np.all(mask, axis=0)
                im = im[:, mask, :]
            return im, win
        elif out == 'fh':
            win.getScreenshot(fh)
            return
        
    def display(self):
        r"""
        Function to display the ampActor within in an interactable 
        vtkRenWin window
        
        Returns
        -------
        win: vtkRenWin
            The generated vtkRenWin
        
        """
        if not hasattr(self, 'actor'):
            self.addActor()
        # Generate a renderer window
        win = vtkRenWin()
        # Set the number of viewports
        win.setnumViewports(1)
        # Set the background colour
        win.setBackground([1,1,1])
        # Set camera projection 
        renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(win)
        renderWindowInteractor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        # Set camera projection 
        win.setView()
        win.renderActors([self.actor,])
        win.Render()
        win.rens[0].GetActiveCamera().Azimuth(0)
        win.rens[0].GetActiveCamera().SetParallelProjection(True)
        win.Render()
        return win


    def addActor(self, CMap=None, bands=128, sRange=[0,8]):
        r"""
        Creates an ampActor based upon the ampObject 
        
        """
        self.actor = ampActor()
        #self._v = numpy_support.numpy_to_vtk(self.vert, deep=0)
        self.actor.setVert(self.vert)
        self.actor.setFaces(self.faces)
        self.actor.setNorm()
        # Test if values array is non-zero
        if self.values.any():
            self.actor.setValues(self.values)
            self.createCMap()
            if self.values.min() < 0:
                self.actor.setCMap(self.CMapN2P, bands)
                self.actor.setScalarRange([self.values.min(), self.values.max()])
                self.actor.Mapper.SetLookupTable(self.actor.lut)
            else: 
                self.actor.setCMap(self.CMap02P, bands)
                self.actor.setScalarRange([0, self.values.max()])
                self.actor.Mapper.SetLookupTable(self.actor.lut)

    def createCMap(self, cmap=None, n = 50):
        r"""
        Function to generate a linear colormap for the AmpObj based upon 
        base colours 
        
        cmap: array_like
            The rgb float values of the base colors used to generate the 
            colormap
        n: int, default 50
            The number of bands that form the colormap

        """
        if cmap is None:
            c1 = [31.0, 73.0, 125.0]
            c3 = [170.0, 75.0, 65.0]
            c2 = [212.0, 221.0, 225.0]
            CMap1 = np.c_[[np.linspace(st, en) for (st, en) in zip(c1, c2)]]
            CMap2 = np.c_[[np.linspace(st, en) for (st, en) in zip(c2, c3)]]
            CMap = np.c_[CMap1[:, :-1], CMap2]
            self.CMapN2P = np.transpose(CMap)/255.0
            self.CMap02P = np.flip(np.transpose(CMap1)/255.0, axis=0)
        

class ampActor(vtk.vtkActor):
    r"""
    A wrapper around the classic vtkActor that makes it easier to transfer 
    data from the ampObject 
    """

    def __init__(self, CMap=None, bands=128):
        super(ampActor, self).__init__()
        self.mesh = vtk.vtkPolyData()
        self.points = vtk.vtkPoints()
        self.polys = vtk.vtkCellArray()
        self.Mapper = vtk.vtkPolyDataMapper()
        #self.setVert(data['vert'])
        #self.setFaces(data['faces'])
        #self.setNorm()
        #if CMap is not None:
        #    self.setRect(data['values'])
        #    self.setCMap(CMap, bands)
        self.Mapper.InterpolateScalarsBeforeMappingOn()
        self.Mapper.SetInputData(self.mesh)
        #if CMap is not None:
        #    self.setScalarRange()
        #    self.Mapper.SetLookupTable(self.lut)
        self.SetMapper(self.Mapper)
        

    def setVert(self, vert, deep=0):
        """
        Set the vertices of the ampActor
        
        Parameters
        ----------
        vert: ndarray
            The numpy array specifying the vertices 
        deep: int, default 0
            If 1, the numpy array will be deep-copied to the ampActor
        
        """
        self._v = numpy_support.numpy_to_vtk(vert, deep=deep)
        self.points.SetData(self._v)
#            self.points.SetData(vert)
        self.mesh.SetPoints(self.points)
        
    def setFaces(self, faces, deep=0):
        r"""
        Sets the faces of the ampActor
        
        Parameters
        ----------
        faces: ndarray
            The numpy array specifying the faces, or connectivity index based
            upon the vertex array
        deep: int, default 0
            If 1, the numpy array will be deep-copied to the ampActor
        """
        self._faces = np.c_[np.tile(faces.shape[1], faces.shape[0]),
                            faces].flatten().astype(np.int64)
        self._f = numpy_support.numpy_to_vtkIdTypeArray(self._faces, deep=deep)
        self.polys.SetCells(len(faces), self._f)
        self.mesh.SetPolys(self.polys)
    
    def setNorm(self, norm=None, deep=0):
        r"""
        Sets or calculates the vertex normals 
        
        Parameters
        ----------
        norm: ndarray, default None
            The numpy array specifying the face normals. If None, the inbuilt 
            vtk method will be used to calculate the normals
        deep: int, default 0
            If 1, the numpy array will be deep-copied to the ampActor

        """
        if norm is not None:
            self._n = numpy_support.numpy_to_vtk(norm, deep=deep)
            self.mesh.GetPointData().SetNormals(self._n)
        else:
            self.norm = vtk.vtkPolyDataNormals()
            self.norm.ComputePointNormalsOn()
            self.norm.ComputeCellNormalsOff()
            self.norm.SetFeatureAngle(30.0)
            self.norm.SetInputData(self.mesh)
            self.norm.Update()
            self.mesh.DeepCopy(self.norm.GetOutput())
        self.GetProperty().SetInterpolationToGouraud()

    def setValues(self, values, deep=0):
        """
        Set the values of the ampActor
        
        Parameters
        ----------
        values: ndarray
            Scalar data attached to each vertex
        deep: int, default 0
            If 1, the numpy array will be deep-copied to the ampActor
        
        """
        self._values = numpy_support.numpy_to_vtk(values, deep=deep)
        self.mesh.GetPointData().SetScalars(self._values)
        
    def setOpacity(self, opacity=1.0):
        r"""
        Sets the opacity of the ampActor
        
        Parameters
        ----------
        opacity: float, default 1.0
            Opacity value between [0 1]
        """
        self.GetProperty().SetOpacity(opacity)
        
    def setColor(self, color=[1.0, 1.0, 1.0]):
        r"""
        Sets the color of the ampActor
        
        Parameters
        ----------
        color: array_like, default [1.0, 1.0, 1.0]
            The RGB values as floats of the ampActor colour between [0, 1]
        
        """
        self.GetProperty().SetColor(color)
        
    def setScalarRange(self, sRange):
        r"""
        Sets the scalar range on the ampActor
        
        Parameters
        ----------
        sRange: array_like
            Specifies the lower and upper bound of the scalar range to display
        """
        self.Mapper.SetScalarRange(sRange[0], sRange[1])
        

    def setCMap(self, CMap, bands=128):
        r"""
        Sets the colormap used to display scalar values
        
        Parameters
        ----------
        CMap: array_like
            The base colors used to define the color map
        bands: int, default 128
            The number of contour bands to divide up the color map
        """
        self.ctf = vtk.vtkColorTransferFunction()
        self.ctf.SetColorSpaceToDiverging()
        for ind, point in zip(np.linspace(0, 1, len(CMap)), CMap):
            self.ctf.AddRGBPoint(ind, point[0], point[1], point[2])
        self.lut = vtk.vtkLookupTable()
        self.lut.SetNumberOfTableValues(bands)
        self.lut.Build()
        for i in range(bands):
            rgb = list(self.ctf.GetColor(float(i) / bands)) + [1]
            self.lut.SetTableValue(i, rgb)
        self.Mapper.SetLookupTable(self.lut)
    
    def setShading(self, shading=True):
        r"""
        Sets whether shading is used on the ampActor
        
        Parameters
        ----------
        shading: boolean, default True
            If True, shading is used in the display of the ampActor
        """
        if shading is True:
            self.GetProperty().LightingOn()
        if shading is False:
            self.GetProperty().LightingOff()

    def addSlices(self, slices):
        r"""
        Adds slices into the AmpActor which can then be rendered 

        Parameters
        ----------
        slices: array_like
            The values in the z-axis of which to make the slices 
        """
        self.planes = []
        self.cutters = []
        self.pMapper = []
        self.pActors = []
        self.lActors = []
        self.labels = []
        self.hier = []
        self.lMapper = []
        for s in slices:
            p = vtk.vtkPlane()
            p.SetOrigin(0, 0, s)
            p.SetNormal(0, 0, 1)
            c = vtk.vtkCutter()
            c.SetCutFunction(p)
            c.SetInputData(self.mesh)
            c.Update()
            cM=vtk.vtkPolyDataMapper()
            cM.SetInputConnection(c.GetOutputPort())
            pA=vtk.vtkActor()
            pA.GetProperty().SetColor(31.0/255.0, 73.0/255.0, 125.0/255.0)
            pA.GetProperty().SetLineWidth(5)
            pA.GetProperty().SetInterpolationToFlat()
            pA.GetProperty().EdgeVisibilityOn()
            pA.GetProperty().SetRenderLinesAsTubes(True)
            pA.SetMapper(cM)

            text = vtk.vtkBillboardTextActor3D()
            text.SetInput('test')
            text.SetPosition(0,0,s)
            text.GetTextProperty().SetColor(0, 0, 0)


            self.planes.append(p)
            self.cutters.append(c)
            self.pMapper.append(cM)
            self.pActors.append(pA)
            self.lActors.append(text)
        self.setOpacity(0.1)


