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
                circleRadius = 4
                circleThikness = -1
                lineThikness = 2
            else:
                circleRadius = 3
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


def GetBezierSpline(loPoint, startMP = 0.0, endMP = 1.0, MPStep = 0.01):
    assert 0.0 <= startMP < endMP <= 1.0
    assert 0.0 < MPStep < 1.0

    loRstPoint = list()
    if len(loPoint) >= 2:
        pointNum = len(loPoint)
        n = pointNum - 1
        loCoeff = list()
        for coeffIdx in range(pointNum):
            coeff = numpy.math.factorial(n) / numpy.math.factorial(coeffIdx) / numpy.math.factorial(n - coeffIdx)
            loCoeff.append(coeff)

        loMP = numpy.arange(startMP, endMP + MPStep, MPStep)
        for MP in loMP:
            if 0.0 <= MP <= 1.0:
                x = 0
                y = 0
                for coeffIdx, coeff in enumerate(loCoeff):
                    coeff *= numpy.math.pow(1 - MP, n - coeffIdx)
                    coeff *= numpy.math.pow(MP, coeffIdx)

                    x += loPoint[coeffIdx][0] * coeff
                    y += loPoint[coeffIdx][1] * coeff

                point = numpy.array((x, y), numpy.float)
                loRstPoint.append(point)
    elif len(loPoint) == 1:
        loRstPoint.append(loPoint[0])
    else:
        loRstPoint = None

    return loRstPoint

class bezierSplineDemo_c:
    @staticmethod
    def MouseCB(event, x, y, flag, self):
        assert isinstance(self, bezierSplineDemo_c)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.bezierSpline.AddPoint((x, y))
            self.UpdateCanvas(True)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.bezierSpline.PopPoint()
            self.UpdateCanvas(True)

    def __init__(self, winName = "BezierSpline", canvasWidth = 800, canvasHeight = 600, loPoint = None):
        self.winName = winName
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight

        if loPoint is None:
            loPoint = ((50, 50), (canvasWidth / 2, canvasHeight - 50), (canvasWidth - 50, 50))

        self.bezierSpline = bezierSpline_c(loPoint)
        self.trace = self.bezierSpline.GetTrace()

        self.canvas = numpy.full((self.canvasHeight, self.canvasWidth, 3), 0, numpy.uint8)

    def UpdateCanvas(self, pointChanged=False):
        self.canvas.setfield(255, numpy.uint8)
        self.bezierSpline.Draw(self.canvas, self.loColor)

        if pointChanged:
            self.trace = GetBezierSpline(self.bezierSpline.loPointList[0])
        if self.trace is not None:
            color = self.loColor[self.bezierSpline.levelNum - 1]
            for pointIdx in range(len(self.trace) - 1):
                startPoint = bezierSpline_c.PointToTuple(self.trace[pointIdx])
                endPoint = bezierSpline_c.PointToTuple(self.trace[pointIdx + 1])
                cv2.line(self.canvas, startPoint, endPoint, color, 2)

        cv2.imshow(self.winName, self.canvas)

    def Run(self):
        cv2.namedWindow(self.winName, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.winName, bezierSplineDemo_c.MouseCB, self)

        self.loColor = list()
        for i in range(10):
            color = (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))
            self.loColor.append(color)

        def UpdateMovePercent(val):
            movePercent = float(val) / 100.0

            self.bezierSpline.UpdateMidPoint(movePercent)

            self.UpdateCanvas()

        cv2.createTrackbar("Percent", self.winName, 0, 100, UpdateMovePercent)
        UpdateMovePercent(0)

        cv2.waitKey(0)

        cv2.destroyWindow(self.winName)

    def Animation(self):
        cv2.namedWindow(self.winName, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.winName, bezierSplineDemo_c.MouseCB, self)

        self.loColor = list()
        for i in range(10):
            color = (random.randint(0, 250), random.randint(0, 250), random.randint(0, 250))
            self.loColor.append(color)

        dMP = 0.01
        MP = 0.0
        while True:
            self.bezierSpline.UpdateMidPoint(MP)
            self.UpdateCanvas()

            MP += dMP
            if MP > 1.0:
                MP = 1.0
                dMP = -dMP
            elif MP < 0.0:
                MP = 0.0
                dMP = -dMP


            key = cv2.waitKey(50)
            if key == ord('f'):
                break
            elif key == ord('+'):
                dMP *= 2.0
                if abs(dMP) >= 0.5:
                    dMP = dMP / abs(dMP) * 0.5
            elif key == ord('-'):
                dMP /= 2.0
                if abs(dMP) <= 0.01:
                    dMP = dMP / abs(dMP) * 0.01

        cv2.destroyWindow(self.winName)