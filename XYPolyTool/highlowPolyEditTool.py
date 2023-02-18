#encoding:utf-8
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

class highlowPolyEdit():

	ListOfLowPoly = []

	#DeBug	
	def DeBugPrint(self,*args):
		print(self.ListOfLowPoly)
		print(self.GetHightPolyList())

	#按UV边平滑=====================================================================================
	def SoftByUVsEdge(self,*args):
		ObjList = cmds.ls(sl=1, o=1) or []
		for SubObj in ObjList:
			cmds.select(SubObj)
			cmds.polyNormalPerVertex(ufn=1) #解冻法线
			cmds.polySoftEdge(a=0,ch=1) #硬化所有边

			mel.eval("ConvertSelectionToUVs") #选择所有的uv点      
			
			NumbOfUVShell = cmds.polyEvaluate( uvShell=True )#获得uv壳的数量      
			
			ListOfUVs = cmds.ls(sl=1,fl=1) #获取UVs的列表       
			
			UVShellIndices = cmds.polyEvaluate( uvShellIds=True ) #获取UVs所在壳的ID    

			#创建对应数量的壳集合放到总的集合中
			ListOfUvShellList = []
			for i in range(NumbOfUVShell):
				ListOfUvShellList.append([]) 

			#将UVs添加到对应的壳集合中
			UVsIndex = 0
			for uvs in ListOfUVs:
				ListOfUvShellList[UVShellIndices[UVsIndex]].append(uvs)
				UVsIndex += 1    

			#将每个壳中对应的UVs转换为内部边
			for ListOfUVsInOneShell in ListOfUvShellList:
				EdgeInShell = cmds.polyListComponentConversion(ListOfUVsInOneShell,te=1,internal=1)
				cmds.polySoftEdge(EdgeInShell,a=180,ch=1)
		
		cmds.select(ObjList)

	#重命名===========================================================================================
	def Rename(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		NewName = cmds.textField('RenameTextField', q=1, tx = 1)
		StartNumb = cmds.textField('StartTextField', q=1, tx = 1)
		PaddingNumb = cmds.textField('PaddingTextField', q=1, tx = 1)

		NameNumb = StartNumb.zfill(int(PaddingNumb)) #获取指定位数的起始编号

		for EachObj in ListOfSelected:
			cmds.rename(EachObj, NewName + NameNumb)
			NameNumb = str(int(NameNumb)+1).zfill(int(PaddingNumb))

	#添加后缀
	@staticmethod
	def AddSuffix(poly):
		ListOfSelected = cmds.ls(sl=1) or []
		SuffixText = cmds.textField(poly, q=1, tx = 1)

		for EachObj in ListOfSelected:
			if '|' in EachObj:
				EachObjName = EachObj.rsplit('|',1)[1]
			else:
				EachObjName = EachObj

			cmds.rename(EachObj,EachObjName+SuffixText)

	def AddLowSuffix(self,*args):
		self.AddSuffix(poly='LowSubfixTextField')

	#删除后缀
	def DeletLowSuffix(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		SuffixText = cmds.textField('LowSubfixTextField', q=1, tx = 1)

		for EachObj in ListOfSelected:
			if '|' in EachObj:
				EachObjName = EachObj.rsplit('|',1)[1]
			else:
				EachObjName = EachObj

			cmds.rename(EachObj,EachObjName.rstrip(SuffixText))

	#记录低模
	def RecordLowPoly(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		LowPolySuffix = cmds.textField('LowSubfixTextField', q=1, tx = 1)
		#检查是不是按照格式命好名了
		for EachObj in ListOfSelected:
			CheckSuffix = EachObj.endswith(LowPolySuffix)
			if CheckSuffix ==False:
				raise Exception(EachObj+' lowpoly formate is incorrect! ')
		self.ListOfLowPoly = ListOfSelected
		om.MGlobal.displayInfo('Record Lowpoly Successfully')
		SliderMaxValue = len(self.ListOfLowPoly)
		cmds.intSlider('CheckSlider',e=1, max=SliderMaxValue)
		#启用功能
		'''
		cmds.button('ShowAll', e=1, enable=1)
		cmds.checkBoxGrp('VisHideLowHigh', e=1, enable=1)
		cmds.button('ChooseLowPoly', e=1, enable=1)		
		cmds.button('ChooseHighPoly',e=1,  enable=1)
		cmds.button('ChooseBothPoly', e=1, enable=1)
		cmds.button('CheckMatchButton', e=1, enable=1)
		cmds.intSlider('CheckSlider', e=1, enable=1)
		'''
		cmds.columnLayout('FunctionAfterRecord', e=1, enable=1)

	#匹配高低模重命名高模===============================================================================
	def MatchHighLowPoly(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		LowPolySuffix = cmds.textField('LowSubfixTextField', q=1, tx = 1)
		HighPolySuffix = cmds.textField('HighSubfixTextField', q=1, tx = 1)
		#检查选中项
		if len(ListOfSelected) != 2: #是否选中了两项
			raise Exception('Please select two object, one is lowpoly, another is highpoly to match!')

		if ListOfSelected[0].endswith(LowPolySuffix) ==  ListOfSelected[1].endswith(LowPolySuffix): #是否选择了两个低模或者都不是低模
			raise Exception('You choose two lowpoly, or you are not choose lowpoly!')

		if ListOfSelected[0] not in self.ListOfLowPoly and ListOfSelected[1] not in self.ListOfLowPoly:
			raise Exception('You are not choose lowpoly which has recorded!')
			
		#确定谁是低模
		if ListOfSelected[0].endswith(LowPolySuffix) == True:
			LowPoly = ListOfSelected[0]
			HighPoly = ListOfSelected[1]
		else:
			LowPoly = ListOfSelected[1]
			HighPoly = ListOfSelected[0]

		#检查低模是否被记录
		if LowPoly not in self.ListOfLowPoly:
			raise Exception('The low poly have not been recorded!')

		#匹配后隐藏
		if cmds.checkBox('HideAferMatchCheckBox', q=1, v=1) == 1:
			cmds.hide(ListOfSelected)

		#确定高模的名字
		HighPolyName = LowPoly.replace(LowPolySuffix,HighPolySuffix)
		cmds.rename(HighPoly,HighPolyName)

	#设置快捷键========================================================================================
	def SetMatchHotkey(self,*args):
		#判断热键集,否则就创建一个
		if cmds.hotkeySet( q=True, current=True ) == 'Maya_Default':
			cmds.hotkeySet( 'MyKeySet', current=True )

		#创建命令
		cmds.nameCommand( 'SetMatchHotkey', ann='Match High Low Poly', c='python("MatchTool.MatchHighLowPoly()")' )
		#获取快捷键
		KeyShortcut = cmds.textField('Hotkey', query = 1, tx = 1)
		CtrlValue = cmds.checkBoxGrp( 'HotKeyAttach', query = 1, value3 = 1)
		AltValue = cmds.checkBoxGrp( 'HotKeyAttach', query = 1, value1 = 1)
		ShiftValue = cmds.checkBoxGrp( 'HotKeyAttach', query = 1, value2 = 1)

		#检查快捷键是否已经被设置
		if cmds.hotkey(KeyShortcut, q=1, alt=AltValue, sht=ShiftValue, ctl=CtrlValue) == False:
			cmds.hotkey( k = KeyShortcut, alt=AltValue, sht=ShiftValue, ctl=CtrlValue, name='SetMatchHotkey' )
		else:
			raise Exception('The hotkey has attached command!')
		om.MGlobal.displayInfo('Set hotkey successfully')


	#显示隐藏高低模====================================================================================
	#通过低模得到对应的高模
	@staticmethod
	def GetHighPolyByLowPoly(LowPolyName):
		LowPolySuffix = cmds.textField('LowSubfixTextField', q=1, tx = 1)
		HighPolySuffix = cmds.textField('HighSubfixTextField', q=1, tx = 1)

		HighPolyName = LowPolyName.replace(LowPolySuffix,HighPolySuffix)

		return HighPolyName

	#检查高低模是否都成对了
	
	def CheckMatch(self,LowPoly):
		HighPoly = self.GetHighPolyByLowPoly(LowPolyName=LowPoly)
		return cmds.objExists(HighPoly)

	def CheckListMatch(self, *args):
		for EachPoly in self.ListOfLowPoly:
			if self.CheckMatch(EachPoly) == False:
				raise Exception(EachPoly+' do not have matched highpoly!')
		om.MGlobal.displayInfo('Congratulations! Each lowpoly has matched highpoly')
		cmds.text('CheckSliderText',e=1, enable=1)
		cmds.intSlider('CheckSlider',e=1, enable=1)
	
	#获得高模的列表
	def GetHightPolyList(self, *args):
		ListOfHighPoly = []
		for EachPoly in self.ListOfLowPoly:
			HighPoly = self.GetHighPolyByLowPoly(LowPolyName=EachPoly)
			ListOfHighPoly.append(HighPoly)
		return ListOfHighPoly

	#显示高低模
	def ShowAll(self, *args):
		ListOfHighPoly = self.GetHightPolyList()
		for EachPoly in ListOfHighPoly:
			try:
				cmds.showHidden(EachPoly)
			except:
				pass
		for EachPoly in self.ListOfLowPoly:
				cmds.showHidden(EachPoly)

		cmds.checkBoxGrp( 'VisHideLowHigh',e=1, valueArray2=[1, 1], enable=1)
	#分组显示隐藏

	def ShowHideLow (self, *args):
		if cmds.checkBoxGrp( 'VisHideLowHigh', q=1, v1=1) ==1:
			cmds.showHidden(self.ListOfLowPoly)
		else:
			cmds.hide(self.ListOfLowPoly)

	def ShowHideHigh (self, *args):
		ListOfHighPoly = self.GetHightPolyList()
		if cmds.checkBoxGrp( 'VisHideLowHigh', q=1, v2=1) ==1:
			for EachPoly in ListOfHighPoly:
				try:
					cmds.showHidden(EachPoly)
				except:
					pass
		else:
			for EachPoly in ListOfHighPoly:
				try:
					cmds.hide(EachPoly)
				except:
					pass

	#滑动检查==========================================================================================
	#隐藏所用
	def HideAll(self, *args):
		ListOfHighPoly = self.GetHightPolyList()
		for EachPoly in ListOfHighPoly:
			try:
				cmds.hide(EachPoly)
			except:
				pass
		for EachPoly in self.ListOfLowPoly:
				cmds.hide(EachPoly)
	#滑条功能
	def ShowMatchedHighLowSlider(self, *args):
		SliderValue = cmds.intSlider('CheckSlider', q=1, v=1)
		if SliderValue == 0:
			self.ShowAll()
		else:
			self.HideAll()
			index = SliderValue-1
			lowpoly = self.ListOfLowPoly[index]
			highpoly = self.GetHighPolyByLowPoly(LowPolyName=lowpoly)
			try:
				cmds.showHidden(lowpoly,highpoly)
			except:
				pass

	#快速选择==========================================================================================
	def SelectLowPoly(self, *args):
		cmds.select(self.ListOfLowPoly)

	def SelectHighPoly(self, *args):
		cmds.select(self.GetHightPolyList())

	def SelectHighLowPoly(self, *args):
		cmds.select(self.ListOfLowPoly+self.GetHightPolyList())

	#UI===============================================================================================
	def highlowPolyEditUI(self,*args,**kwargs):

		#日常窗口检查
		if cmds.window('highlowPolyEditToolWindow',query=1,exists=1):
			  cmds.deleteUI('highlowPolyEditToolWindow')

		#创建窗口
		cmds.window('highlowPolyEditToolWindow',title='XYPolyTool v1.0')
		cmds.columnLayout(adjustableColumn=True)

		cmds.separator( height=5, style='none' )

		#平滑低模UV----------------------------------------------------------------------
		cmds.columnLayout()
		cmds.text(l=' 低模按UV边界平滑内部边', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='选中并平滑', h=40, c=self.SoftByUVsEdge)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=5, style='none' )

		#重命名-------------------------------------------------------------------------
		cmds.columnLayout()
		cmds.text(l=' 重命名低模', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=2, adj=2)
		cmds.text(l='名称:', w=55, al='right')
		cmds.textField('RenameTextField', tx='objName')
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=5, adj=3)
		cmds.text(l='起始编号:', w=55, al='right')
		cmds.textField('StartTextField', tx='1', w=90)
		cmds.text(l='')
		cmds.text(l='编号位数:', w=55, al='right')
		cmds.textField('PaddingTextField', tx='2', w=90)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='重命名低模', h=40, c=self.Rename)
		cmds.setParent('..')

		cmds.separator( height=5, style='in' )

		#设置低模的格式
		cmds.columnLayout()
		cmds.text(l=' 设置低模格式', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=5, adj=2)
		cmds.text(l='后缀名:', w=55, al='right')
		cmds.textField('LowSubfixTextField', tx='_low')
		cmds.text(l='', w=5)
		cmds.button(l='删除', w=45, c=self.DeletLowSuffix)
		cmds.button(l='添加', w=45, c=self.AddLowSuffix)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='选中低模并记录', h=40, c=self.RecordLowPoly)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=5, style='none')

		#匹配并重命名高模------------------------------------------------------------------------
		cmds.columnLayout('FunctionAfterRecord',enable=0,adjustableColumn=True)

		cmds.columnLayout()
		cmds.text(l=' 设置高模格式', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=4,adj=2)
		cmds.text(l='后缀名:', w=55, al='right')
		cmds.textField('HighSubfixTextField', tx='_high')
		cmds.text(l='', w=5)
		cmds.checkBox('HideAferMatchCheckBox',l='匹配后隐藏',v=1, w=90)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='同时选中高低模进行重命名匹配', h=40, c=self.MatchHighLowPoly)
		cmds.setParent('..')

		cmds.separator( height=5, style='in' )

		#设置快捷键
		cmds.columnLayout()
		cmds.text(l=' 为该功能设置快捷键', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=5,adj=3)
		cmds.text(l='', w=5)
		cmds.checkBoxGrp( 'HotKeyAttach',numberOfCheckBoxes=3, labelArray3=['alt', 'shift', 'ctrl'],cw3=[40,50,40],valueArray3=[1, 1, 0])
		cmds.textField('Hotkey', tx='w', w=20)
		cmds.text(l='', w=5)
		cmds.button(l='设置快捷键', w=90, c=self.SetMatchHotkey)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=5, style='none')

		#显示隐藏高低模
		cmds.rowColumnLayout(numberOfColumns=4,adj=4)
		cmds.text(l='', w=5)
		cmds.checkBoxGrp( 'VisHideLowHigh',numberOfCheckBoxes=2, enable=0,labelArray2=['显示低模', '显示高模'],valueArray2=[1, 1],cc1=self.ShowHideLow,cc2=self.ShowHideHigh)
		cmds.text(l='')
		cmds.button('ShowAll', l='全部显示', w=80, enable=1, c=self.ShowAll)
		cmds.setParent('..')

		#cmds.separator( height=5, style='none' )

		#检查高低模匹配
		cmds.columnLayout()
		cmds.text(l=' 检查高低模匹配', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowLayout(numberOfColumns=1, adj=1)
		cmds.button('CheckMatchButton', enable=1, l='检查匹配情况',c=self.CheckListMatch)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		#滑动查看匹配
		cmds.rowLayout(numberOfColumns=2, adj=2)
		cmds.text('CheckSliderText',l=' 滑动查看匹配',enable=0)
		cmds.intSlider('CheckSlider', enable=0, min=0,v=0,step=1,dc=self.ShowMatchedHighLowSlider)
		cmds.setParent('..')

		cmds.separator( height=5, style='in' )

		#选择高低模
		cmds.rowLayout(numberOfColumns=3, adj=3)
		cmds.button('ChooseLowPoly', enable=1, l='选择低模', w=75, c=self.SelectLowPoly)		
		cmds.button('ChooseHighPoly', enable=1, l='选择高模', w=75, c=self.SelectHighPoly)
		cmds.button('ChooseBothPoly', enable=1, l='全选', c=self.SelectHighLowPoly)
		cmds.setParent('..')

		cmds.setParent('..')
		'''
		#Debug
		cmds.separator( height=20, style='in' )
		cmds.button(l='Debug',c=self.DeBugPrint)
		'''

		#窗口收尾
		cmds.window('highlowPolyEditToolWindow', e=True, w=300, h=1)
		cmds.showWindow('highlowPolyEditToolWindow')
