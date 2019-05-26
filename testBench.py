import cv2, numpy
import sys, random, copy

class bezierSpline_c:
    @staticmethod
    def CalcMidPoint(startPoint, endPoint, movePercent, midPoint=None):
        assert isinstance(movePercent, float)
        assert 0.0 <= movePercent <= 1.0

        midX = float(startPoint[0]) + (float(endPoint[0]) - float(startPoint[0])) * movePercent
        midY = float(startPoint[1]) + (float(endPoint[1]) - float(startPoint[1])) * movePercent

        if midPoint is not None:
            midPoint[0] = midX
            midPoint[1] = midY
        else:
            midPoint = numpy.array((midX, midY), numpy.float)
            return midPoint

    @staticmethod
    def PointToTuple(point):
        assert isinstance(point, numpy.ndarray)
        assert point.ndim == 1
        assert len(point) == 2

        return (int(point[0]), int(point[1]))

    def __init__(self, loPoint = None):
        self.loPointList = list()

        loBaseLevelPoint = list()
        if loPoint is not None:
            for point in loPoint:
                assert len(point) == 2
                point = numpy.array(point, numpy.float)
                loBaseLevelPoint.append(point)

        self.loPointList.append(loBaseLevelPoint)

        self.levelNum = len(loBaseLevelPoint)

        for level in range(1, self.levelNum):
            loMidPoint = [numpy.zeros(2, numpy.float) for i in range(self.levelNum - level)]
            self.loPointList.append(loMidPoint)

        self.UpdateMidPoint(0.0)



    def UpdateMidPoint(self, movePercent):
        assert isinstance(movePercent, float)
        assert 0.0 <= movePercent <= 1.0

        self.movePercent = movePercent

        for level in range(0, self.levelNum - 1):
            loCurLevelPoint = self.loPointList[level]
            loNextLevelPoint = self.loPointList[level + 1]
            for startPointIdx in range(len(loCurLevelPoint) - 1):
                startPoint = loCurLevelPoint[startPointIdx]
                endPoint = loCurLevelPoint[startPointIdx + 1]
                midPoint = loNextLevelPoint[startPointIdx]

                self.CalcMidPoint(startPoint, endPoint, self.movePercent, midPoint)


    def AddPoint(self, point):
        assert len(point) == 2
        self.loPointList[0].append(numpy.array(point, numpy.float))
        self.levelNum += 1

        if self.levelNum >= 2:
            self.loPointList.append(list())

        for level in range(0, self.levelNum - 1):
            loCurLevelPoint = self.loPointList[level]
            loNextLevelPoint = self.loPointList[level + 1]

            startPoint = loCurLevelPoint[-2]
            endPoint = loCurLevelPoint[-1]
            midPoint = self.CalcMidPoint(startPoint, endPoint, self.movePercent)

            loNextLevelPoint.append(midPoint)

    def PopPoint(self):
        for level in range(0, self.levelNum):
            self.loPointList[level].pop(-1)

        if self.levelNum >= 2:
            self.loPointList.pop(-1)

        if self.levelNum >= 1:
            self.levelNum -= 1

    def GetTrace(self, startMP = 0.0, endMP = 1.0, MPStep = 0.01):
        if self.levelNum >= 2:
            trace = list()
            MP = self.movePercent
            loMP = numpy.arange(startMP, endMP, MPStep)
            for curMP in loMP:
                self.UpdateMidPoint(curMP)
                trace.append(copy.deepcopy(self.loPointList[-1][0]))
            self.UpdateMidPoint(MP)
        else:
            trace = None

        return trace

    def Draw(self, canvas, loColor = None):
        if loColor is None:
            loColor = list()
        for i in range(0, self.levelNum - len(loColor)):
            color = (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))
            loColor.append(color)

        for level in range(self.levelNum):
            if level == self.levelNum - 1:
                circleRadius = 3
                circleThikness = -1
                lineThikness = 3
            else:
                circleRadius = 2
                circleThikness = 1
                lineThikness = 1

            loCurLevelPoint = self.loPointList[level]
            curColor = loColor[level]
            for point in loCurLevelPoint:
                center = self.PointToTuple(point)
                cv2.circle(canvas, center, circleRadius, curColor, circleThikness)

            for startPointIdx in range(len(loCurLevelPoint) - 1):
                startPoint = self.PointToTuple(loCurLevelPoint[startPointIdx])
                endPoint = self.PointToTuple(loCurLevelPoint[startPointIdx + 1])
                cv2.line(canvas, startPoint, endPoint, curColor, lineThikness)




if __name__ == "__main__":
    bezierSpline = bezierSpline_c(((0, 0), (10, 20), (40, 50)))
    trace = bezierSpline.GetTrace()

    canvasWidth = 400
    canvasHeight = 300

    canvas = numpy.full((canvasHeight, canvasWidth, 3), 0, numpy.uint8)

    winName = "BezierSpline"
    cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)

    loColor = list()
    for i in range(10):
        color = (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))
        loColor.append(color)

    def UpdateCanvas(pointChanged = False):
        canvas.setfield(255, numpy.uint8)
        bezierSpline.Draw(canvas, loColor)

        global trace
        if pointChanged:
            trace = bezierSpline.GetTrace()
        if trace is not None:
            color = loColor[bezierSpline.levelNum - 1]
            for point in trace:
                center = bezierSpline_c.PointToTuple(point)
                cv2.circle(canvas, center, 1, color, 1)

        cv2.imshow(winName, canvas)

    def UpdateMovePercent(val):
        movePercent = float(val) / 100.0

        bezierSpline.UpdateMidPoint(movePercent)

        UpdateCanvas()

    cv2.createTrackbar("Percent", winName, 0, 100, UpdateMovePercent)
    trace = bezierSpline.GetTrace()
    UpdateMovePercent(0)

    def MouseCB(event, x, y, flag, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            bezierSpline.AddPoint((x, y))
            UpdateCanvas(True)
        elif event == cv2.EVENT_RBUTTONDOWN:
            bezierSpline.PopPoint()
            UpdateCanvas(True)



    cv2.setMouseCallback(winName, MouseCB, None)

    cv2.waitKey(0)
    pass