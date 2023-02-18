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

	#��UV��ƽ��=====================================================================================
	def SoftByUVsEdge(self,*args):
		ObjList = cmds.ls(sl=1, o=1) or []
		for SubObj in ObjList:
			cmds.select(SubObj)
			cmds.polyNormalPerVertex(ufn=1) #�ⶳ����
			cmds.polySoftEdge(a=0,ch=1) #Ӳ�����б�

			mel.eval("ConvertSelectionToUVs") #ѡ�����е�uv��      
			
			NumbOfUVShell = cmds.polyEvaluate( uvShell=True )#���uv�ǵ�����      
			
			ListOfUVs = cmds.ls(sl=1,fl=1) #��ȡUVs���б�       
			
			UVShellIndices = cmds.polyEvaluate( uvShellIds=True ) #��ȡUVs���ڿǵ�ID    

			#������Ӧ�����ĿǼ��Ϸŵ��ܵļ�����
			ListOfUvShellList = []
			for i in range(NumbOfUVShell):
				ListOfUvShellList.append([]) 

			#��UVs��ӵ���Ӧ�ĿǼ�����
			UVsIndex = 0
			for uvs in ListOfUVs:
				ListOfUvShellList[UVShellIndices[UVsIndex]].append(uvs)
				UVsIndex += 1    

			#��ÿ�����ж�Ӧ��UVsת��Ϊ�ڲ���
			for ListOfUVsInOneShell in ListOfUvShellList:
				EdgeInShell = cmds.polyListComponentConversion(ListOfUVsInOneShell,te=1,internal=1)
				cmds.polySoftEdge(EdgeInShell,a=180,ch=1)
		
		cmds.select(ObjList)

	#������===========================================================================================
	def Rename(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		NewName = cmds.textField('RenameTextField', q=1, tx = 1)
		StartNumb = cmds.textField('StartTextField', q=1, tx = 1)
		PaddingNumb = cmds.textField('PaddingTextField', q=1, tx = 1)

		NameNumb = StartNumb.zfill(int(PaddingNumb)) #��ȡָ��λ������ʼ���

		for EachObj in ListOfSelected:
			cmds.rename(EachObj, NewName + NameNumb)
			NameNumb = str(int(NameNumb)+1).zfill(int(PaddingNumb))

	#��Ӻ�׺
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

	#ɾ����׺
	def DeletLowSuffix(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		SuffixText = cmds.textField('LowSubfixTextField', q=1, tx = 1)

		for EachObj in ListOfSelected:
			if '|' in EachObj:
				EachObjName = EachObj.rsplit('|',1)[1]
			else:
				EachObjName = EachObj

			cmds.rename(EachObj,EachObjName.rstrip(SuffixText))

	#��¼��ģ
	def RecordLowPoly(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		LowPolySuffix = cmds.textField('LowSubfixTextField', q=1, tx = 1)
		#����ǲ��ǰ��ո�ʽ��������
		for EachObj in ListOfSelected:
			CheckSuffix = EachObj.endswith(LowPolySuffix)
			if CheckSuffix ==False:
				raise Exception(EachObj+' lowpoly formate is incorrect! ')
		self.ListOfLowPoly = ListOfSelected
		om.MGlobal.displayInfo('Record Lowpoly Successfully')
		SliderMaxValue = len(self.ListOfLowPoly)
		cmds.intSlider('CheckSlider',e=1, max=SliderMaxValue)
		#���ù���
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

	#ƥ��ߵ�ģ��������ģ===============================================================================
	def MatchHighLowPoly(self,*args):
		ListOfSelected = cmds.ls(sl=1) or []
		LowPolySuffix = cmds.textField('LowSubfixTextField', q=1, tx = 1)
		HighPolySuffix = cmds.textField('HighSubfixTextField', q=1, tx = 1)
		#���ѡ����
		if len(ListOfSelected) != 2: #�Ƿ�ѡ��������
			raise Exception('Please select two object, one is lowpoly, another is highpoly to match!')

		if ListOfSelected[0].endswith(LowPolySuffix) ==  ListOfSelected[1].endswith(LowPolySuffix): #�Ƿ�ѡ����������ģ���߶����ǵ�ģ
			raise Exception('You choose two lowpoly, or you are not choose lowpoly!')

		if ListOfSelected[0] not in self.ListOfLowPoly and ListOfSelected[1] not in self.ListOfLowPoly:
			raise Exception('You are not choose lowpoly which has recorded!')
			
		#ȷ��˭�ǵ�ģ
		if ListOfSelected[0].endswith(LowPolySuffix) == True:
			LowPoly = ListOfSelected[0]
			HighPoly = ListOfSelected[1]
		else:
			LowPoly = ListOfSelected[1]
			HighPoly = ListOfSelected[0]

		#����ģ�Ƿ񱻼�¼
		if LowPoly not in self.ListOfLowPoly:
			raise Exception('The low poly have not been recorded!')

		#ƥ�������
		if cmds.checkBox('HideAferMatchCheckBox', q=1, v=1) == 1:
			cmds.hide(ListOfSelected)

		#ȷ����ģ������
		HighPolyName = LowPoly.replace(LowPolySuffix,HighPolySuffix)
		cmds.rename(HighPoly,HighPolyName)

	#���ÿ�ݼ�========================================================================================
	def SetMatchHotkey(self,*args):
		#�ж��ȼ���,����ʹ���һ��
		if cmds.hotkeySet( q=True, current=True ) == 'Maya_Default':
			cmds.hotkeySet( 'MyKeySet', current=True )

		#��������
		cmds.nameCommand( 'SetMatchHotkey', ann='Match High Low Poly', c='python("MatchTool.MatchHighLowPoly()")' )
		#��ȡ��ݼ�
		KeyShortcut = cmds.textField('Hotkey', query = 1, tx = 1)
		CtrlValue = cmds.checkBoxGrp( 'HotKeyAttach', query = 1, value3 = 1)
		AltValue = cmds.checkBoxGrp( 'HotKeyAttach', query = 1, value1 = 1)
		ShiftValue = cmds.checkBoxGrp( 'HotKeyAttach', query = 1, value2 = 1)

		#����ݼ��Ƿ��Ѿ�������
		if cmds.hotkey(KeyShortcut, q=1, alt=AltValue, sht=ShiftValue, ctl=CtrlValue) == False:
			cmds.hotkey( k = KeyShortcut, alt=AltValue, sht=ShiftValue, ctl=CtrlValue, name='SetMatchHotkey' )
		else:
			raise Exception('The hotkey has attached command!')
		om.MGlobal.displayInfo('Set hotkey successfully')


	#��ʾ���ظߵ�ģ====================================================================================
	#ͨ����ģ�õ���Ӧ�ĸ�ģ
	@staticmethod
	def GetHighPolyByLowPoly(LowPolyName):
		LowPolySuffix = cmds.textField('LowSubfixTextField', q=1, tx = 1)
		HighPolySuffix = cmds.textField('HighSubfixTextField', q=1, tx = 1)

		HighPolyName = LowPolyName.replace(LowPolySuffix,HighPolySuffix)

		return HighPolyName

	#���ߵ�ģ�Ƿ񶼳ɶ���
	
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
	
	#��ø�ģ���б�
	def GetHightPolyList(self, *args):
		ListOfHighPoly = []
		for EachPoly in self.ListOfLowPoly:
			HighPoly = self.GetHighPolyByLowPoly(LowPolyName=EachPoly)
			ListOfHighPoly.append(HighPoly)
		return ListOfHighPoly

	#��ʾ�ߵ�ģ
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
	#������ʾ����

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

	#�������==========================================================================================
	#��������
	def HideAll(self, *args):
		ListOfHighPoly = self.GetHightPolyList()
		for EachPoly in ListOfHighPoly:
			try:
				cmds.hide(EachPoly)
			except:
				pass
		for EachPoly in self.ListOfLowPoly:
				cmds.hide(EachPoly)
	#��������
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

	#����ѡ��==========================================================================================
	def SelectLowPoly(self, *args):
		cmds.select(self.ListOfLowPoly)

	def SelectHighPoly(self, *args):
		cmds.select(self.GetHightPolyList())

	def SelectHighLowPoly(self, *args):
		cmds.select(self.ListOfLowPoly+self.GetHightPolyList())

	#UI===============================================================================================
	def highlowPolyEditUI(self,*args,**kwargs):

		#�ճ����ڼ��
		if cmds.window('highlowPolyEditToolWindow',query=1,exists=1):
			  cmds.deleteUI('highlowPolyEditToolWindow')

		#��������
		cmds.window('highlowPolyEditToolWindow',title='XYPolyTool v1.0')
		cmds.columnLayout(adjustableColumn=True)

		cmds.separator( height=5, style='none' )

		#ƽ����ģUV----------------------------------------------------------------------
		cmds.columnLayout()
		cmds.text(l=' ��ģ��UV�߽�ƽ���ڲ���', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='ѡ�в�ƽ��', h=40, c=self.SoftByUVsEdge)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=5, style='none' )

		#������-------------------------------------------------------------------------
		cmds.columnLayout()
		cmds.text(l=' ��������ģ', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=2, adj=2)
		cmds.text(l='����:', w=55, al='right')
		cmds.textField('RenameTextField', tx='objName')
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=5, adj=3)
		cmds.text(l='��ʼ���:', w=55, al='right')
		cmds.textField('StartTextField', tx='1', w=90)
		cmds.text(l='')
		cmds.text(l='���λ��:', w=55, al='right')
		cmds.textField('PaddingTextField', tx='2', w=90)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='��������ģ', h=40, c=self.Rename)
		cmds.setParent('..')

		cmds.separator( height=5, style='in' )

		#���õ�ģ�ĸ�ʽ
		cmds.columnLayout()
		cmds.text(l=' ���õ�ģ��ʽ', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=5, adj=2)
		cmds.text(l='��׺��:', w=55, al='right')
		cmds.textField('LowSubfixTextField', tx='_low')
		cmds.text(l='', w=5)
		cmds.button(l='ɾ��', w=45, c=self.DeletLowSuffix)
		cmds.button(l='���', w=45, c=self.AddLowSuffix)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='ѡ�е�ģ����¼', h=40, c=self.RecordLowPoly)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=5, style='none')

		#ƥ�䲢��������ģ------------------------------------------------------------------------
		cmds.columnLayout('FunctionAfterRecord',enable=0,adjustableColumn=True)

		cmds.columnLayout()
		cmds.text(l=' ���ø�ģ��ʽ', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=4,adj=2)
		cmds.text(l='��׺��:', w=55, al='right')
		cmds.textField('HighSubfixTextField', tx='_high')
		cmds.text(l='', w=5)
		cmds.checkBox('HideAferMatchCheckBox',l='ƥ�������',v=1, w=90)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		cmds.rowColumnLayout(numberOfColumns=1, adj=1)
		cmds.button(l='ͬʱѡ�иߵ�ģ����������ƥ��', h=40, c=self.MatchHighLowPoly)
		cmds.setParent('..')

		cmds.separator( height=5, style='in' )

		#���ÿ�ݼ�
		cmds.columnLayout()
		cmds.text(l=' Ϊ�ù������ÿ�ݼ�', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowColumnLayout(numberOfColumns=5,adj=3)
		cmds.text(l='', w=5)
		cmds.checkBoxGrp( 'HotKeyAttach',numberOfCheckBoxes=3, labelArray3=['alt', 'shift', 'ctrl'],cw3=[40,50,40],valueArray3=[1, 1, 0])
		cmds.textField('Hotkey', tx='w', w=20)
		cmds.text(l='', w=5)
		cmds.button(l='���ÿ�ݼ�', w=90, c=self.SetMatchHotkey)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=3, style='in' ,)
		cmds.separator( height=5, style='none')

		#��ʾ���ظߵ�ģ
		cmds.rowColumnLayout(numberOfColumns=4,adj=4)
		cmds.text(l='', w=5)
		cmds.checkBoxGrp( 'VisHideLowHigh',numberOfCheckBoxes=2, enable=0,labelArray2=['��ʾ��ģ', '��ʾ��ģ'],valueArray2=[1, 1],cc1=self.ShowHideLow,cc2=self.ShowHideHigh)
		cmds.text(l='')
		cmds.button('ShowAll', l='ȫ����ʾ', w=80, enable=1, c=self.ShowAll)
		cmds.setParent('..')

		#cmds.separator( height=5, style='none' )

		#���ߵ�ģƥ��
		cmds.columnLayout()
		cmds.text(l=' ���ߵ�ģƥ��', h=20, fn ='boldLabelFont')
		cmds.setParent('..')

		cmds.rowLayout(numberOfColumns=1, adj=1)
		cmds.button('CheckMatchButton', enable=1, l='���ƥ�����',c=self.CheckListMatch)
		cmds.setParent('..')

		cmds.separator( height=5, style='none' )

		#�����鿴ƥ��
		cmds.rowLayout(numberOfColumns=2, adj=2)
		cmds.text('CheckSliderText',l=' �����鿴ƥ��',enable=0)
		cmds.intSlider('CheckSlider', enable=0, min=0,v=0,step=1,dc=self.ShowMatchedHighLowSlider)
		cmds.setParent('..')

		cmds.separator( height=5, style='in' )

		#ѡ��ߵ�ģ
		cmds.rowLayout(numberOfColumns=3, adj=3)
		cmds.button('ChooseLowPoly', enable=1, l='ѡ���ģ', w=75, c=self.SelectLowPoly)		
		cmds.button('ChooseHighPoly', enable=1, l='ѡ���ģ', w=75, c=self.SelectHighPoly)
		cmds.button('ChooseBothPoly', enable=1, l='ȫѡ', c=self.SelectHighLowPoly)
		cmds.setParent('..')

		cmds.setParent('..')
		'''
		#Debug
		cmds.separator( height=20, style='in' )
		cmds.button(l='Debug',c=self.DeBugPrint)
		'''

		#������β
		cmds.window('highlowPolyEditToolWindow', e=True, w=300, h=1)
		cmds.showWindow('highlowPolyEditToolWindow')
