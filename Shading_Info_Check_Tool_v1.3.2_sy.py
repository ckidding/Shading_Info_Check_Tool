# -*- coding:utf-8 -*-
# !/usr/bin/env python

# 作者：宋羽（小K）
# 联系方式：
## 微信: ckidding
## QQ：360074528
## 邮箱: conan-song@qq.com

import maya.cmds as mc
import sys

def findShapeLs():
    shadeByObjLs  = []
    shadeByFaceLs = []
    MTLostLs      = []
    objHasUselessShapeLs = []

    shapeLs = mc.ls(g=1,l=1)
    shadedObj = []
    for i in shapeLs:
        if mc.nodeType(i) != 'nurbsCurve':
            shadedObj.append(i)

    for shape in shadedObj:
        #shape = mc.ls(sl=1,dag=1,s=1)[0]
        
        #选物体上的材质，只有.instObjGroups[0]上有SG
        #选面上的材质，.compInstObjGroups.compObjectGroups、.instObjGroups[0].objectGroups上都有SG

        OG = mc.listConnections(shape+'.instObjGroups[0]')
        IOG = mc.listConnections(shape+'.instObjGroups[0].objectGroups')
        CIOG = mc.listConnections(shape+'.compInstObjGroups[0].compObjectGroups')
        #print OG,IOG,CIOG
        
        #transformNode = mc.listRelatives(shape,p=1)[0]
        
        if OG != None:
            #print 'by obj !'
            shadeByObjLs.append(shape)
        else:
            #if (IOG == None and CIOG == None) or (IOG == None and CIOG != None):
            SGLs = []
            if IOG == None:
                MTLostLs.append(shape)
            else:
                for ele in IOG:
                    if mc.nodeType(ele) == 'shadingEngine':
                        SGLs.append(ele)
                if SGLs == []:
                    #print 'MT lost !!!'
                    MTLostLs.append(shape)
                else:
                    #print 'by face !'
                    shadeByFaceLs.append(shape)
                    ##instObjGroups、.compInstObjGroups上都有SG的物体，若comp和ins上没有一样的SG，comp上的SG可以删掉
                    ##此时comp上的SG是最开始选物体上的SG，是为了防止其他SG断掉后材质丢失的情况
                    sameNodeLs = []
                    SGLs = []
                    if CIOG != [] and CIOG != None:
                        for ele in CIOG:
                            if mc.nodeType(ele) == 'shadingEngine':
                                SGLs.append(ele)
                        if SGLs != []:
                            for i in SGLs:
                                if i in IOG:
                                    sameNodeLs.append(i)
                            if sameNodeLs == [] :
                                #print 'object has useless SG on shape'
                                objHasUselessShapeLs.append(shape)
    '''
    print 'shadeByObjLs =  ',           shadeByObjLs
    print 'shadeByFaceLs =  ',          shadeByFaceLs
    print 'objHasUselessShapeLs =  ',   objHasUselessShapeLs
    print 'MTLostLs =  ',               MTLostLs
    
    '''
    return shadeByObjLs,shadeByFaceLs,objHasUselessShapeLs,MTLostLs
    #MTLostLs为选物体上材质，材质丢失的情况
'''
print 'shadeByObjLs =  ',           findShapeLs()[0]
print 'shadeByFaceLs =  ',          findShapeLs()[1]
print 'objHasUselessShapeLs =  ',   findShapeLs()[2]
print 'MTLostLs =  ',               findShapeLs()[3]
'''

#不能P给window，弃用
'''
def findMTLostObj_byFace():
    #判断所有物体的每个面有无材质丢失
    shadedObj = []
    MTLostObjLs = []
    shapeLs = mc.ls(g=1,l=1)
    for i in shapeLs:
        if mc.nodeType(i) != 'nurbsCurve' and mc.nodeType(i) != 'nurbsSurface':
            shadedObj.append(i)
    amount = 0.00
    if shadedObj != []:
        mc.progressWindow(title='Searching Faces...',
                    progress=amount,
                    status='Searching: 0%',
                    isInterruptable=True)
        for obj in shadedObj:
            objSG_ls = []
            for node in mc.listConnections(obj):
                if mc.nodeType(node) == 'shadingEngine':
                    objSG_ls.append(node)

            objFaceLs = mc.ls(mc.polyListComponentConversion(obj,tf=1),fl=1)
            judge = 1
            for face in objFaceLs:
                #当前判断的面和当前判断的材质没关系时，向judgeLs中加0
                #len(judgeLs) == len(objSG_ls)时，没有材质匹配，材质丢失
                judgeLs = []
                for index in range(len(objSG_ls)):
                    if mc.sets(face, isMember=objSG_ls[index]) == 0:
                        judgeLs.append(0)
                if len(judgeLs) == len(objSG_ls):
                    if obj not in MTLostObjLs:
                        MTLostObjLs.append(obj)
            
            amount += round(100.0/len(shadedObj), 2)
            mc.progressWindow(edit=True, progress=round(amount,2), status=('Searching: ' + `round(amount,0)` + '%' ))
        mc.progressWindow(endProgress=1)
    
    return MTLostObjLs
'''
def findMTLostObj_byFace():
    global window_clean
    #判断所有物体的每个面有无材质丢失，包含SG上MT丢失的情况
    if mc.pluginInfo('redshift4maya',q=1,l=1) == 0:
        mc.confirmDialog(title='Warning', icon='warning', message= '\nRedshift unloaded !',
                         button='ok', defaultButton='ok', cancelButton='ok', dismissString='ok',p=window_clean)
        return
    shadedObj = []
    MTLostObjLs = []
    shapeLs = mc.ls(g=1,l=1)
    for i in shapeLs:
        if mc.nodeType(i) != 'nurbsCurve' and mc.nodeType(i) != 'nurbsSurface':
            shadedObj.append(i)

    if shadedObj != []:
        amount = 0.0
        windowName = 'progress'
        if mc.objExists(mc.window(windowName,q=1,ex=1)):
            mc.deleteUI(windowName)
        progressWindow = mc.window(t=windowName,widthHeight=(300, 50))
        mc.columnLayout()
        tx = mc.text(l='Seaching for material missing objects: 0.0 %',w=300)
        
        progressControl = mc.progressBar(progress=amount,w=300)
        mc.showWindow(progressWindow)

        for obj in shadedObj:
            objSG_ls = []
            objConnct = mc.listConnections(obj)
            if objConnct != None:
                for node in objConnct:
                    if mc.nodeType(node) == 'shadingEngine':
                        objSG_ls.append(node)
                if objSG_ls != []:
                    for SG in objSG_ls:
                        if mc.listConnections(SG + '.rsSurfaceShader') == None and mc.listConnections(SG + '.surfaceShader') == None:
                            if obj not in MTLostObjLs:
                                MTLostObjLs.append(obj)
            objFaceLs = mc.ls(mc.polyListComponentConversion(obj,tf=1),fl=1)
            judge = 1

            for face in objFaceLs:
                #当前判断的面和当前判断的材质没关系时，向judgeLs中加0
                #len(judgeLs) == len(objSG_ls)时，没有材质匹配，材质丢失
                polyShape = mc.listRelatives(face,p=1)[0]
                judgeLs = []
                
                for index in range(len(objSG_ls)):
                    if mc.sets(face, isMember=objSG_ls[index]) == 0 and mc.sets(polyShape, isMember=objSG_ls[index]) == 0:
                        judgeLs.append(0)

                if len(judgeLs) == len(objSG_ls):
                    if obj not in MTLostObjLs:
                        MTLostObjLs.append(obj)

            amount += 100.0/len(shadedObj)
            mc.progressBar(progressControl,edit=True,progress=amount,status=('Seaching for material missing objects: ' + `amount` + '%' ))
            mc.text(tx,e=1,l='Seaching for material missing objects: ' + `round(amount,0)` + ' %')
        #mc.progressBar(progressControl,edit=True,endProgress=1)#只有maya左下角主面板有用
        mc.deleteUI(progressWindow)

        return MTLostObjLs


def clickButton_cmd(index):
    currentSlLs = mc.textScrollList('objLs',q=1,ai=1)
    if currentSlLs != [] and currentSlLs != None:
        mc.textScrollList('objLs', e=1, ra = 1)
    objLs = findShapeLs()[index]
    if objLs == []:
        mc.textScrollList('objLs', e=1, append = 'None')
    else:
        for obj in objLs:
            mc.textScrollList('objLs', e=1, append = obj)
    if index ==3:
        MTLostObj = findMTLostObj_byFace()
        if MTLostObj != []:
            for obj in MTLostObj:
                if 'None' in mc.textScrollList('objLs',q=1,ai=1):
                    mc.textScrollList('objLs',e=1,ra=1)
                if obj not in mc.textScrollList('objLs',q=1,ai=1):
                    mc.textScrollList('objLs', e=1, append = obj)


def selectObj_cmd():
    inputLs = mc.textScrollList('objLs',q=1,si=1)
    if inputLs != None:
        if 'None' not in inputLs:
            transLs = []
            for i in inputLs:
                transLs.append(mc.listRelatives(i,p=1)[0])
            mc.select(transLs)

        
def selectAllInLs_cmd():
    objInLs = mc.textScrollList('objLs',q=1,ai=1)
    if objInLs != None:
        if 'None' not in objInLs:
            mc.textScrollList('objLs',e=1,si=objInLs)
            selectObj_cmd()

#双击时取消选择
def deSelectObj_cmd():
    inputLs = mc.textScrollList('objLs',q=1,si=1)
    if 'None' not in inputLs:
        mc.select(inputLs,cl=1)
        mc.textScrollList('objLs',e=1,di= mc.textScrollList('objLs',q=1,si=1))


def removeSlInLs_cmd():
    slObjLs=mc.textScrollList('objLs',q=True,si=1)
    if slObjLs != None:
        if 'None' not in slObjLs:
            mc.textScrollList('objLs',e=True,ri=slObjLs)
            mc.select(slObjLs,cl=1)

def removeAllInLs_cmd():
    mc.textScrollList('objLs',e=True,ra=1)
    ls = mc.textScrollList('objLs',q=True,ai=1)
    if ls != None:
        if 'None' not in ls:
            mc.select(ls,cl=1)
    mc.textScrollList('objLs',e=True,a='None')
    
def deSelectAllInLs_cmd():
    mc.textScrollList('objLs',e=True,da=1)
    ls = mc.textScrollList('objLs',q=True,ai=1)
    if ls != None:
        if 'None' not in ls:
            mc.select(ls,cl=1)


#断开Useless SG On列表内选中物体的多余SG节点
#移除断开后的Useless SG On列表，并提示
##shape和SG的属性链接没有好的方法得到，现用循环10以内的序号得到

def disconnctUselessSG():
    connectionLs = []
    shapeWithUselessSGLs = mc.textScrollList('objLs',q=1,si=1)
    
    reminder_sy_1 = 'Select objects with useless SG on in the list bellow !\n( 请选中useless SG on列表内的物体！)'
    reminder_sy_2 = 'No usless SG nodes on objects !\n( 物体上没有多余SG节点！)'
    UselessSGOnLs = findShapeLs()[2]
    
    #如果没有多余SG节点链接，提示
    if UselessSGOnLs == []:
        mc.confirmDialog(title='Info', p=shadingInfoWindow,icon='information',message= reminder_sy_2, button='ok')
        return 
    #如果没有选中，提示
    if shapeWithUselessSGLs == None or shapeWithUselessSGLs == []:
        mc.confirmDialog(title='Info', p=shadingInfoWindow,icon='information',message= reminder_sy_1, button='ok') 
        return
    #如果选中的物体不在Useless SG On的列表内，提示
    for i in shapeWithUselessSGLs:
        if i not in UselessSGOnLs:
            mc.confirmDialog(title='Info', p=shadingInfoWindow,icon='information',message= reminder_sy_1, button='ok') 
            sys.exit()
            
    for shape in shapeWithUselessSGLs:
        shapeShort = shape.rsplit("|", 1)[1]
        desConnctLs = mc.listConnections(shapeShort+'.compInstObjGroups[0].compObjectGroups')
        SG_ls = []
        for node in desConnctLs:
            if mc.nodeType(node) == 'shadingEngine':
                SG_ls.append(node)
        if SG_ls != []:
            for SG_Node in SG_ls:
                #print SG_Node
                attributesMaxIndex = 10
                for i in range(attributesMaxIndex):
                    for j in range(attributesMaxIndex):
                        if mc.connectionInfo(SG_Node + '.dagSetMembers[' + str(i) + ']',sfd=1) == shapeShort+'.compInstObjGroups[0].compObjectGroups['+ str(j) +']':
                            SG_attr = SG_Node + '.dagSetMembers[' + str(i) + ']'
                            shape_attr = shapeShort+'.compInstObjGroups[0].compObjectGroups['+ str(j) +']'
                            if SG_attr not in connectionLs:
                                connectionLs.append(SG_attr)
                                connectionLs.append(shape_attr)
    LsLen = len(connectionLs)
    a=0
    reminderLs = []
    for i in range(LsLen/2):
        mc.disconnectAttr(connectionLs[a+1],connectionLs[a])
        
        #记录断开连接的两端节点
        shapeNode = connectionLs[a+1].split('.',1)[0]
        SGName = connectionLs[a].split('.',1)[0]
        
        if (shapeNode + '    and    ' +  SGName) not in reminderLs:
            reminderLs.append(shapeNode + '    and    ' +  SGName)
        a+=2
    
    #去掉表中选中的项
    mc.textScrollList('objLs',e=1,ri=mc.textScrollList('objLs',q=1,si=1))
    
    #提示断开连接的节点
    reminderString = columnList(reminderLs)
    reminderWindow(reminderString)
    
def columnList(list):
    outStr = ''
    for i in list:
        outStr += str(i)+'\r\n'

    return outStr

def reminderWindow(word):
    window_name = 'Disconnection_Info'
    window_title = 'Disconnection Info'
    height = 300
    width = 300
    if(mc.window(window_name,q=1,ex=1)):mc.deleteUI(window_name)
    mc.window(window_name,t=window_title,ret=1,mb=1,w=width,p=shadingInfoWindow)
    mc.scrollLayout()
    mc.text('Disconnections between these nodes have been done:')
    mc.text('(已断开这些节点间的链接:)\n\n')
    mc.text(word)
    mc.setParent('..')
    mc.showWindow(window_name)

def helpWindow():
    window_name = 'Help'
    window_title = window_name
    if(mc.window(window_name,q=1,ex=1)):mc.deleteUI(window_name)
    mc.window(window_name,t=window_title,ret=1,mb=1,w=300,p=shadingInfoWindow)

    height = 20
    width = 180
    mc.frameLayout('',lv=0)
    mc.text('Shading By Object  ( 选物体上材质的模型 )',h=height)
    mc.text('Shading By Faces  ( 选面上材质的模型 )',h=height)
    mc.text('Materials Missing  ( 材质丢失的模型 )',h=height)
    mc.text('Useless SG On  ( 连有多余SG节点的模型 )',h=height)
    mc.text('Disconnect Useless SG  ( 断开多余SG节点 )',h=height)
    mc.text('Select All  ( 选中列表内所有物体 )',h=height)
    mc.text('Deselect All  ( 对列表内所有物体取消选择 )',h=height)
    mc.text('Remove Selected  ( 移除列表内选中的物体 )',h=height)
    mc.text('Clear All  ( 移除列表内所有物体 )',h=height)
    mc.setParent('..')
    mc.showWindow(window_name)

def mainWindow():
    global shadingInfoWindow
    main_window_name = 'Shading_Info'
    window_title = 'Shading Info Check Tool v1.3_sy'
    if(mc.window(main_window_name,q=1,ex=1)):mc.deleteUI(main_window_name)
    shadingInfoWindow = mc.window(main_window_name,t=window_title,ret=1,mb=1,w=300)

    bleed = 4
    width = 180
    mc.frameLayout('',lv=0)

    mc.columnLayout(adj=1)
    mc.rowLayout(adj=1,nc=3)
    mc.button('Shaded By Object',w=width/3*2,c='clickButton_cmd(0)')
    mc.button('Shaded By Faces',w=width/3*2,c='clickButton_cmd(1)')
    mc.button('Materials Missing',w=width/3*2,c='clickButton_cmd(3)')
    mc.setParent('..')
    mc.setParent('..')

    mc.columnLayout( adj=1 )
    mc.rowLayout(adj=1,nc=2)
    mc.button('Useless SG On',w=width,c='clickButton_cmd(2)')
    mc.button('Disconnect Useless SG',w=width,c='disconnctUselessSG()')
    mc.setParent('..')
    mc.setParent('..')

    mc.columnLayout( adj=1 )
    mc.rowLayout(adj=1,nc=4)
    mc.button('Select All',w=width/2,c='selectAllInLs_cmd()')
    mc.button('Deselect All',w=width/2,c='deSelectAllInLs_cmd()')
    mc.button('Remove Selected',w=width/2,c='removeSlInLs_cmd()')
    mc.button('Clear All',w=width/2,c='removeAllInLs_cmd()')
    mc.setParent('..')
    mc.setParent('..')

    mc.textScrollList('objLs', numberOfRows=20, h=200,allowMultiSelection=True ,sc='selectObj_cmd()',dcc='deSelectObj_cmd()',dkc='removeSlInLs_cmd()')
    mc.setParent('..')

    mc.setParent('..')

    mc.columnLayout( adj=1 )
    mc.button('Help',c='helpWindow()')
    mc.setParent('..')
    mc.showWindow(shadingInfoWindow)


mainWindow()