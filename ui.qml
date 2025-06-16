// ui.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtGraphicalEffects 1.15

ApplicationWindow {
    id: mainWindow
    width: 1200
    height: 800
    visible: true
    title: "学生管理系统"
    
    // 颜色定义
    readonly property color backgroundColor: "#f5f5f7"
    readonly property color cardColor: "#ffffff"
    readonly property color borderColor: "#e0e0e0"
    readonly property color textColor: "#333333"
    readonly property color accentColor: "#007AFF"
    readonly property color dangerColor: "#FF3B30"
    readonly property color successColor: "#4CD964"
    readonly property color warningColor: "#FF9500"
    
    // 通知颜色 (全局变量)
    property color notificationColor: accentColor
    
    // 编辑模式标志
    property bool isEditMode: false
    
    // 学生数据模型
    ListModel {
        id: studentModel
    }
    
    // 背景
    Rectangle {
        anchors.fill: parent
        color: backgroundColor
        
        // 添加简单的渐变效果
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#f8f8fa" }
            GradientStop { position: 1.0; color: "#f0f0f5" }
        }
    }
    
    // 标题栏
    Rectangle {
        id: titleBar
        width: parent.width
        height: 60
        color: cardColor
        
        // 添加轻微阴影
        layer.enabled: true
        layer.effect: DropShadow {
            verticalOffset: 2
            radius: 8.0
            samples: 17
            color: Qt.rgba(0, 0, 0, 0.1)
        }
        
        Text {
            text: "学生管理系统"
            font.pixelSize: 22
            font.weight: Font.Medium
            color: textColor
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 30
        }
        
        // 窗口控制按钮
        Row {
            anchors.right: parent.right
            anchors.rightMargin: 20
            anchors.verticalCenter: parent.verticalCenter
            spacing: 12
            
            Rectangle {
                width: 28
                height: 28
                radius: width / 2
                color: Qt.rgba(1, 0.8, 0, 0.8)
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: mainWindow.showMinimized()
                    
                    Rectangle {
                        width: 12
                        height: 2
                        color: "white"
                        anchors.centerIn: parent
                    }
                }
            }
            
            Rectangle {
                width: 28
                height: 28
                radius: width / 2
                color: Qt.rgba(1, 0.3, 0.3, 0.8)
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: Qt.quit()
                    
                    Text {
                        text: "×"
                        color: "white"
                        font.pixelSize: 16
                        font.weight: Font.Bold
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }
    
    // 主要内容区域
    Item {
        id: contentArea
        anchors.top: titleBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20
        
        // 操作工具栏
        RowLayout {
            id: toolbar
            width: parent.width
            spacing: 15
              // 添加学生按钮
            Button {
                text: "添加学生"
                onClicked: addStudentDialog.open()
                
                background: Rectangle {
                    implicitWidth: 120
                    implicitHeight: 40
                    radius: 8
                    color: accentColor
                }
                
                contentItem: Text {
                    text: "添加学生"
                    color: "white"
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            // 统计按钮
            Button {
                text: "成绩统计"
                onClicked: {
                    // 直接打开对话框，让onOpened事件处理统计数据获取
                    statisticsDialog.open();
                }
                
                background: Rectangle {
                    implicitWidth: 120
                    implicitHeight: 40
                    radius: 8
                    color: warningColor
                }
                
                contentItem: Text {
                    text: "成绩统计"
                    color: "white"
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            // 搜索框
            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "搜索学生..."
                
                background: Rectangle {
                    implicitHeight: 40
                    radius: 8
                    color: cardColor
                    border.color: borderColor
                    border.width: 1
                }
                
                onTextChanged: {
                    if (text.length > 0) {
                        filteredModel.clear();
                        for (var i = 0; i < studentModel.count; i++) {
                            var student = studentModel.get(i);
                            if (student.name.toLowerCase().includes(text.toLowerCase()) || 
                                student.id.toLowerCase().includes(text.toLowerCase()) ||
                                (student.department && student.department.toLowerCase().includes(text.toLowerCase()))) {
                                filteredModel.append(student);
                            }
                        }
                        studentList.model = filteredModel;
                    } else {
                        studentList.model = studentModel;
                    }
                }
            }
            
            // 清除搜索按钮
            Button {
                text: "清除"
                visible: searchField.text.length > 0
                onClicked: searchField.text = ""
                
                background: Rectangle {
                    implicitWidth: 80
                    implicitHeight: 40
                    radius: 8
                    color: Qt.rgba(0.9, 0.9, 0.9, 1.0)
                }
                
                contentItem: Text {
                    text: "清除"
                    color: textColor
                    font.pixelSize: 14
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
        
        // 搜索结果模型
        ListModel {
            id: filteredModel
        }
        
        // 学生列表
        ListView {
            id: studentList
            anchors.top: toolbar.bottom
            anchors.topMargin: 20
            anchors.bottom: parent.bottom
            width: parent.width
            clip: true
            spacing: 10
            
            // 使用全局ListModel
            model: studentModel
            
            // 设置空列表提示
            Text {
                anchors.centerIn: parent
                text: "暂无学生数据"
                color: Qt.rgba(0, 0, 0, 0.5)
                font.pixelSize: 16
                visible: studentList.count === 0
            }
            
            // 列表项委托
            delegate: Rectangle {
                width: ListView.view.width
                height: 80
                radius: 8
                color: cardColor
                border.color: borderColor
                border.width: 1
                
                // 安全的属性定义
                property string studentId: model ? (model.id || "") : ""
                property string studentName: model ? (model.name || "") : ""
                property string studentGender: model ? (model.gender || "") : ""
                property var studentAge: model ? (model.age || 18) : 18
                property string studentDepartment: model ? (model.department || "") : ""
                property var studentScores: model ? (model.scores || {}) : {}
                
                // 设置阴影
                layer.enabled: true
                layer.effect: DropShadow {
                    horizontalOffset: 0
                    verticalOffset: 2
                    radius: 4.0
                    samples: 9
                    color: Qt.rgba(0, 0, 0, 0.05)
                }
                
                // 点击操作
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        // 将学生数据传递给详情对话框并打开
                        console.log("列表项点击 - 索引:", index)
                        try {
                            var studentData = {
                                id: studentId,
                                name: studentName,
                                gender: studentGender,
                                age: studentAge,
                                department: studentDepartment,
                                scores: studentScores
                            };
                            console.log("处理后的学生数据:", JSON.stringify(studentData))
                            studentDetailDialog.studentData = studentData
                            studentDetailDialog.originalId = studentData.id
                            studentDetailDialog.open()
                        } catch (e) {
                            console.log("列表项点击错误:", e.toString())
                        }
                    }
                }
                
                // 学生信息布局
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 15
                    
                    // 学生头像/标识
                    Rectangle {
                        width: 50
                        height: 50
                        radius: 25
                        color: accentColor
                        
                        Text {
                            anchors.centerIn: parent
                            text: studentName ? studentName.charAt(0) : ""
                            color: "white"
                            font.pixelSize: 20
                            font.weight: Font.Bold
                        }
                    }
                    
                    // 学生信息
                    Column {
                        spacing: 5
                        Layout.fillWidth: true
                        
                        Text {
                            text: studentName
                            font.pixelSize: 16
                            font.weight: Font.Medium
                            color: textColor
                        }
                        
                        Text {
                            text: "学号: " + studentId
                            font.pixelSize: 12
                            color: Qt.rgba(0, 0, 0, 0.6)
                        }
                    }
                    
                    // 其他信息
                    Column {
                        spacing: 5
                        
                        Text {
                            text: studentDepartment
                            font.pixelSize: 14
                            color: Qt.rgba(0, 0, 0, 0.6)
                        }
                        
                        Row {
                            spacing: 5
                            
                            Text {
                                text: studentGender + ", " + studentAge + "岁"
                                font.pixelSize: 12
                                color: Qt.rgba(0, 0, 0, 0.5)
                            }
                            
                            // 显示成绩数量
                            Text {
                                property var scores: studentScores
                                property int scoreCount: {
                                    var count = 0;
                                    for (var key in scores) {
                                        if (scores.hasOwnProperty(key)) count++;
                                    }
                                    return count;
                                }
                                
                                text: scoreCount > 0 ? " | " + scoreCount + "门课程" : ""
                                font.pixelSize: 12
                                color: Qt.rgba(0, 0, 0, 0.5)
                            }
                        }
                    }
                    
                    // 编辑按钮
                    Button {
                        icon.source: "qrc:/icons/edit.png"
                        icon.color: accentColor
                        flat: true
                        
                        background: Rectangle {
                            implicitWidth: 40
                            implicitHeight: 40
                            radius: 20
                            color: "transparent"
                            
                            Rectangle {
                                anchors.centerIn: parent
                                width: 30
                                height: 30
                                radius: 15
                                color: parent.parent.hovered ? Qt.rgba(0, 0, 0, 0.05) : "transparent"
                            }
                        }
                        
                        contentItem: Text {
                            text: "编辑"
                            color: accentColor
                            font.pixelSize: 12
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("编辑按钮点击 - 索引:", index)
                            try {
                                var studentData = {
                                    id: studentId,
                                    name: studentName,
                                    gender: studentGender,
                                    age: studentAge,
                                    department: studentDepartment,
                                    scores: studentScores
                                };
                                console.log("处理后的学生数据:", JSON.stringify(studentData))
                                studentDetailDialog.studentData = studentData
                                studentDetailDialog.originalId = studentData.id
                                studentDetailDialog.isEditMode = true
                                studentDetailDialog.open()
                            } catch (e) {
                                console.log("编辑按钮点击错误:", e.toString())
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 添加学生对话框
    Dialog {
        id: addStudentDialog
        title: "添加新学生"
        width: 500
        height: 600
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.CloseOnEscape
        
        // 设置对话框背景
        background: Rectangle {
            radius: 8
            color: cardColor
            border.color: borderColor
            border.width: 1
        }
        
        // 添加学生表单
        contentItem: Item {
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                // 学生信息表单
                GridLayout {
                    columns: 2
                    columnSpacing: 15
                    rowSpacing: 15
                    Layout.fillWidth: true
                    
                    Text { text: "学号:" }
                    TextField { 
                        id: idField
                        Layout.fillWidth: true 
                        placeholderText: "请输入学号"
                    }
                    
                    Text { text: "姓名:" }
                    TextField { 
                        id: nameField
                        Layout.fillWidth: true 
                        placeholderText: "请输入姓名"
                    }
                    
                    Text { text: "性别:" }
                    ComboBox { 
                        id: genderField
                        model: ["男", "女"]
                        Layout.fillWidth: true 
                    }
                    
                    Text { text: "年龄:" }
                    SpinBox { 
                        id: ageField
                        from: 16
                        to: 30
                        value: 18
                        Layout.fillWidth: true 
                    }
                    
                    Text { text: "院系:" }
                    TextField { 
                        id: departmentField
                        Layout.fillWidth: true 
                        placeholderText: "请输入院系"
                    }
                }
                
                // 考试科目和成绩
                GroupBox {
                    title: "考试科目和成绩"
                    Layout.fillWidth: true
                    
                    GridLayout {
                        columns: 3
                        columnSpacing: 10
                        rowSpacing: 10
                        anchors.fill: parent
                        anchors.margins: 10
                        
                        // 科目1
                        TextField {
                            id: subject1Field
                            Layout.preferredWidth: parent.width * 0.4
                            placeholderText: "科目名称"
                        }
                        
                        SpinBox {
                            id: score1Field
                            from: 0
                            to: 100
                            value: 0
                            Layout.preferredWidth: parent.width * 0.2
                        }
                        
                        Text {
                            text: studentManager ? studentManager.calculate_grade(score1Field.value) : "N/A"
                            color: {
                                if (score1Field.value >= 90) return "#4CAF50" // 绿色
                                if (score1Field.value >= 80) return "#8BC34A" // 浅绿
                                if (score1Field.value >= 70) return "#FFC107" // 黄色
                                if (score1Field.value >= 60) return "#FF9800" // 橙色
                                return "#F44336" // 红色
                            }
                            font.bold: true
                        }
                        
                        // 科目2
                        TextField {
                            id: subject2Field
                            Layout.preferredWidth: parent.width * 0.4
                            placeholderText: "科目名称"
                        }
                        
                        SpinBox {
                            id: score2Field
                            from: 0
                            to: 100
                            value: 0
                            Layout.preferredWidth: parent.width * 0.2
                        }
                        
                        Text {
                            text: studentManager ? studentManager.calculate_grade(score2Field.value) : "N/A"
                            color: {
                                if (score2Field.value >= 90) return "#4CAF50"
                                if (score2Field.value >= 80) return "#8BC34A"
                                if (score2Field.value >= 70) return "#FFC107"
                                if (score2Field.value >= 60) return "#FF9800"
                                return "#F44336"
                            }
                            font.bold: true
                        }
                        
                        // 科目3
                        TextField {
                            id: subject3Field
                            Layout.preferredWidth: parent.width * 0.4
                            placeholderText: "科目名称"
                        }
                        
                        SpinBox {
                            id: score3Field
                            from: 0
                            to: 100
                            value: 0
                            Layout.preferredWidth: parent.width * 0.2
                        }
                        
                        Text {
                            text: studentManager ? studentManager.calculate_grade(score3Field.value) : "N/A"
                            color: {
                                if (score3Field.value >= 90) return "#4CAF50"
                                if (score3Field.value >= 80) return "#8BC34A"
                                if (score3Field.value >= 70) return "#FFC107"
                                if (score3Field.value >= 60) return "#FF9800"
                                return "#F44336"
                            }
                            font.bold: true
                        }
                    }
                }
                
                // 表单操作按钮
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    
                    Button {
                        text: "取消"
                        flat: true
                        onClicked: addStudentDialog.close()
                    }
                    
                    Button {
                        text: "保存"
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: accentColor
                        }
                        
                        contentItem: Text {
                            text: "保存"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            // 表单验证
                            if (!idField.text) {
                                notificationText.text = "请输入学号"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                return
                            }
                            
                            if (!nameField.text) {
                                notificationText.text = "请输入姓名"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                return
                            }
                            
                            // 检查学号是否已存在
                            for (var i = 0; i < studentModel.count; i++) {
                                var existingStudent = studentModel.get(i);
                                if (existingStudent.id === idField.text) {
                                    notificationText.text = "学号 " + idField.text + " 已存在，请使用不同的学号"
                                    notificationColor = dangerColor
                                    notificationAnim.start()
                                    return
                                }
                            }
                            
                            // 创建学生数据
                            var scores = {};
                            
                            // 添加考试科目和成绩
                            if (subject1Field.text) {
                                scores[subject1Field.text] = score1Field.value;
                            }
                            
                            if (subject2Field.text) {
                                scores[subject2Field.text] = score2Field.value;
                            }
                            
                            if (subject3Field.text) {
                                scores[subject3Field.text] = score3Field.value;
                            }
                            
                            var studentData = {
                                id: idField.text,
                                name: nameField.text,
                                gender: genderField.currentText,
                                age: ageField.value,
                                department: departmentField.text,
                                scores: scores
                            };
                            

                            
                            // 尝试保存到数据库
                            try {
                                var success = studentManager.add_student(studentData);
                                if (success) {
                                    // 只有数据库保存成功才添加到模型中
                                    studentModel.append(studentData);
                                    console.log("学生数据保存成功:", JSON.stringify(studentData));
                                } else {
                                    notificationText.text = "保存失败，学号可能已存在，请使用不同的学号"
                                    notificationColor = dangerColor
                                    notificationAnim.start()
                                    return;
                                }
                            } catch (e) {
                                console.log("保存到数据库失败:", e);
                                notificationText.text = "保存失败: " + e.toString()
                                notificationColor = dangerColor
                                notificationAnim.start()
                                return;
                            }
                            
                            // 显示成功通知
                            notificationText.text = "学生添加成功"
                            notificationColor = accentColor
                            notificationAnim.start()
                            
                            // 重置表单
                            idField.text = "";
                            nameField.text = "";
                            departmentField.text = "";
                            subject1Field.text = "";
                            subject2Field.text = "";
                            subject3Field.text = "";
                            score1Field.value = 0;
                            score2Field.value = 0;
                            score3Field.value = 0;
                            
                            // 关闭对话框
                            addStudentDialog.close();
                        }
                    }
                }
            }
        }
    }
    
    // 学生详情/编辑对话框
    Dialog {
        id: studentDetailDialog
        title: isEditMode ? "编辑学生信息" : "学生详情"
        width: 600
        height: 600
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.CloseOnEscape
        
        property var studentData: ({})
        property string originalId: ""
        property bool isEditMode: false
        
        signal dataUpdated()
        
        function fillEditForm() {
            if (studentData && isEditMode) {
                console.log("填充编辑表单:", JSON.stringify(studentData))
                editIdField.text = studentData.id || ""
                editNameField.text = studentData.name || ""
                editGenderField.currentIndex = studentData.gender === "女" ? 1 : 0
                editAgeField.value = studentData.age || 18
                editDepartmentField.text = studentData.department || ""
            }
        }
        
        onOpened: {
            // 每次打开对话框时填充编辑表单
            console.log("对话框打开 - 当前studentData:", JSON.stringify(studentData))
            fillEditForm()
        }
        
        onClosed: {
            isEditMode = false
        }
        
        // 设置对话框背景
        background: Rectangle {
            radius: 8
            color: cardColor
            border.color: borderColor
            border.width: 1
        }
        
        // 学生详情内容
        contentItem: Item {
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                // 学生基本信息卡片
                Rectangle {
                    Layout.fillWidth: true
                    height: studentDetailDialog.isEditMode ? 250 : 120
                    radius: 8
                    color: Qt.rgba(0.97, 0.97, 0.99, 1.0)
                    border.color: borderColor
                    border.width: 1
                    
                    // 编辑模式视图
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 10
                        visible: studentDetailDialog.isEditMode
                        
                        Text {
                            text: "基本信息"
                            font.pixelSize: 16
                            font.weight: Font.Medium
                        }
                        
                        GridLayout {
                            columns: 2
                            columnSpacing: 15
                            rowSpacing: 10
                            Layout.fillWidth: true
                            
                            Text { text: "学号:" }
                            TextField { 
                                id: editIdField
                                Layout.fillWidth: true 
                                placeholderText: "请输入学号"
                            }
                            
                            Text { text: "姓名:" }
                            TextField { 
                                id: editNameField
                                Layout.fillWidth: true 
                                placeholderText: "请输入姓名"
                            }
                            
                            Text { text: "性别:" }
                            ComboBox { 
                                id: editGenderField
                                model: ["男", "女"]
                                Layout.fillWidth: true 
                            }
                            
                            Text { text: "年龄:" }
                            SpinBox { 
                                id: editAgeField
                                from: 16
                                to: 30
                                Layout.fillWidth: true 
                            }
                            
                            Text { text: "院系:" }
                            TextField { 
                                id: editDepartmentField
                                Layout.fillWidth: true 
                                placeholderText: "请输入院系"
                            }
                        }
                    }
                    
                    // 详情模式视图
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 20
                        visible: !studentDetailDialog.isEditMode
                        
                        // 学生头像
                        Rectangle {
                            width: 80
                            height: 80
                            radius: 40
                            color: accentColor
                            
                            Text {
                                anchors.centerIn: parent
                                text: studentDetailDialog.studentData.name ? studentDetailDialog.studentData.name.charAt(0) : ""
                                color: "white"
                                font.pixelSize: 32
                                font.weight: Font.Bold
                            }
                        }
                        
                        // 学生信息
                        GridLayout {
                            columns: 2
                            columnSpacing: 15
                            rowSpacing: 10
                            Layout.fillWidth: true
                            
                            Text { 
                                text: "学号:" 
                                font.pixelSize: 14
                                color: Qt.rgba(0, 0, 0, 0.6)
                            }
                            Text { 
                                text: studentDetailDialog.studentData.id || ""
                                font.pixelSize: 14
                                font.weight: Font.Medium
                            }
                            
                            Text { 
                                text: "姓名:" 
                                font.pixelSize: 14
                                color: Qt.rgba(0, 0, 0, 0.6)
                            }
                            Text { 
                                text: studentDetailDialog.studentData.name || ""
                                font.pixelSize: 14
                                font.weight: Font.Medium
                            }
                            
                            Text { 
                                text: "性别:" 
                                font.pixelSize: 14
                                color: Qt.rgba(0, 0, 0, 0.6)
                            }
                            Text { 
                                text: studentDetailDialog.studentData.gender || ""
                                font.pixelSize: 14
                            }
                            
                            Text { 
                                text: "年龄:" 
                                font.pixelSize: 14
                                color: Qt.rgba(0, 0, 0, 0.6)
                            }
                            Text { 
                                text: studentDetailDialog.studentData.age || ""
                                font.pixelSize: 14
                            }
                            
                            Text { 
                                text: "院系:" 
                                font.pixelSize: 14
                                color: Qt.rgba(0, 0, 0, 0.6)
                            }
                            Text { 
                                text: studentDetailDialog.studentData.department || ""
                                font.pixelSize: 14
                            }
                        }
                        
                        // 编辑切换按钮
                        Button {
                            text: "编辑"
                            
                            background: Rectangle {
                                implicitWidth: 70
                                implicitHeight: 36
                                radius: 6
                                color: accentColor
                            }
                            
                            contentItem: Text {
                                text: "编辑"
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                            }
                            
                            onClicked: {
                                // 切换到编辑模式并填充表单
                                studentDetailDialog.isEditMode = true
                                studentDetailDialog.fillEditForm()
                            }
                        }
                    }
                }
                
                // 考试成绩卡片
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    radius: 8
                    color: Qt.rgba(0.97, 0.97, 0.99, 1.0)
                    border.color: borderColor
                    border.width: 1
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 10
                        
                        // 标题
                        RowLayout {
                            Layout.fillWidth: true
                            
                            Text {
                                text: "考试成绩"
                                font.pixelSize: 16
                                font.weight: Font.Medium
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            Button {
                                text: "添加成绩"
                                
                                background: Rectangle {
                                    implicitWidth: 100
                                    implicitHeight: 30
                                    radius: 4
                                    color: accentColor
                                }
                                
                                contentItem: Text {
                                    text: "添加成绩"
                                    color: "white"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 12
                                }
                                
                                onClicked: {
                                    addScoreDialog.studentId = studentDetailDialog.studentData.id
                                    addScoreDialog.studentIndex = -1
                                    addScoreDialog.open()
                                }
                            }
                        }
                        
                        // 分隔线
                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: borderColor
                        }
                        
                        // 成绩列表
                        ListView {
                            id: scoreListView
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            
                            // 使用成绩数据模型
                            model: {
                                var scoresModel = []
                                var scores = studentDetailDialog.studentData.scores || {}
                                
                                // 将成绩对象转换为数组
                                for (var subject in scores) {
                                    if (scores.hasOwnProperty(subject)) {
                                        scoresModel.push({
                                            subject: subject,
                                            score: scores[subject],
                                            grade: studentManager.calculate_grade(scores[subject])
                                        })
                                    }
                                }
                                
                                return scoresModel
                            }
                            
                            // 成绩项委托
                            delegate: Rectangle {
                                width: scoreListView.width
                                height: 40
                                color: index % 2 === 0 ? Qt.rgba(0.98, 0.98, 1.0, 1.0) : Qt.rgba(1, 1, 1, 1.0)
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 10
                                    spacing: 10
                                    
                                    Text {
                                        text: modelData.subject
                                        Layout.fillWidth: true
                                        font.pixelSize: 14
                                    }
                                    
                                    Text {
                                        text: modelData.score
                                        font.pixelSize: 14
                                        Layout.preferredWidth: 50
                                        horizontalAlignment: Text.AlignRight
                                    }
                                    
                                    Text {
                                        text: modelData.grade
                                        font.pixelSize: 14
                                        Layout.preferredWidth: 30
                                        horizontalAlignment: Text.AlignCenter
                                        font.bold: true
                                        color: {
                                            if (modelData.score >= 90) return "#4CAF50"
                                            if (modelData.score >= 80) return "#8BC34A"
                                            if (modelData.score >= 70) return "#FFC107"
                                            if (modelData.score >= 60) return "#FF9800"
                                            return "#F44336"
                                        }
                                    }
                                    
                                    // 编辑成绩按钮
                                    Button {
                                        icon.source: "qrc:/icons/edit.png" 
                                        icon.color: accentColor
                                        flat: true
                                        implicitWidth: 40
                                        implicitHeight: 30
                                        
                                        background: Rectangle {
                                            implicitWidth: 30
                                            implicitHeight: 30
                                            radius: 4
                                            color: parent.hovered ? Qt.rgba(0, 0, 0, 0.05) : "transparent"
                                        }
                                        
                                        contentItem: Text {
                                            text: "编辑"
                                            color: accentColor
                                            font.pixelSize: 12
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: {
                                            // 打开编辑成绩对话框
                                            addScoreDialog.studentId = studentDetailDialog.studentData.id
                                            addScoreDialog.subjectName = modelData.subject
                                            addScoreDialog.scoreValue = modelData.score
                                            addScoreDialog.studentIndex = index
                                            addScoreDialog.open()
                                        }
                                    }
                                    
                                    // 删除成绩按钮
                                    Button {
                                        icon.source: "qrc:/icons/delete.png"
                                        icon.color: dangerColor
                                        flat: true
                                        implicitWidth: 40
                                        implicitHeight: 30
                                        
                                        background: Rectangle {
                                            implicitWidth: 30
                                            implicitHeight: 30
                                            radius: 4
                                            color: parent.hovered ? Qt.rgba(0, 0, 0, 0.05) : "transparent"
                                        }
                                        
                                        contentItem: Text {
                                            text: "删除"
                                            color: dangerColor
                                            font.pixelSize: 12
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                        
                                        onClicked: {
                                            // 显示确认对话框
                                            deleteScoreConfirmationDialog.studentId = studentDetailDialog.studentData.id
                                            deleteScoreConfirmationDialog.subject = modelData.subject
                                            deleteScoreConfirmationDialog.open()
                                        }
                                    }
                                }
                            }
                            
                            // 无数据时显示的内容
                            Text {
                                anchors.centerIn: parent
                                text: "暂无考试成绩"
                                font.pixelSize: 14
                                color: Qt.rgba(0, 0, 0, 0.4)
                                visible: scoreListView.count === 0
                            }
                        }
                        
                        // 平均成绩
                        RowLayout {
                            Layout.fillWidth: true
                            
                            Text {
                                text: "平均成绩："
                                font.pixelSize: 14
                                font.weight: Font.Medium
                            }
                            
                            Text {
                                text: {
                                    var scores = studentDetailDialog.studentData.scores || {}
                                    var total = 0
                                    var count = 0
                                    
                                    for (var subject in scores) {
                                        if (scores.hasOwnProperty(subject)) {
                                            total += scores[subject]
                                            count++
                                        }
                                    }
                                    
                                    return count > 0 ? (total / count).toFixed(1) : "N/A"
                                }
                                font.pixelSize: 14
                                font.weight: Font.Bold
                                color: {
                                    var avg = 0
                                    var scores = studentDetailDialog.studentData.scores || {}
                                    var total = 0
                                    var count = 0
                                    
                                    for (var subject in scores) {
                                        if (scores.hasOwnProperty(subject)) {
                                            total += scores[subject]
                                            count++
                                        }
                                    }
                                    
                                    if (count > 0) {
                                        avg = total / count
                                        if (avg >= 90) return "#4CAF50"
                                        if (avg >= 80) return "#8BC34A"
                                        if (avg >= 70) return "#FFC107"
                                        if (avg >= 60) return "#FF9800"
                                        return "#F44336"
                                    } else {
                                        return Qt.rgba(0, 0, 0, 0.6)
                                    }
                                }
                            }
                            
                            Text {
                                text: {
                                    var scores = studentDetailDialog.studentData.scores || {}
                                    var total = 0
                                    var count = 0
                                    
                                    for (var subject in scores) {
                                        if (scores.hasOwnProperty(subject)) {
                                            total += scores[subject]
                                            count++
                                        }
                                    }
                                    
                                    if (count > 0) {
                                        var avg = total / count
                                        return " (" + studentManager.calculate_grade(avg) + ")"
                                    } else {
                                        return ""
                                    }
                                }
                                font.pixelSize: 14
                                font.weight: Font.Bold
                                color: {
                                    var avg = 0
                                    var scores = studentDetailDialog.studentData.scores || {}
                                    var total = 0
                                    var count = 0
                                    
                                    for (var subject in scores) {
                                        if (scores.hasOwnProperty(subject)) {
                                            total += scores[subject]
                                            count++
                                        }
                                    }
                                    
                                    if (count > 0) {
                                        avg = total / count
                                        if (avg >= 90) return "#4CAF50"
                                        if (avg >= 80) return "#8BC34A"
                                        if (avg >= 70) return "#FFC107"
                                        if (avg >= 60) return "#FF9800"
                                        return "#F44336"
                                    } else {
                                        return Qt.rgba(0, 0, 0, 0.6)
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 操作按钮
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    
                    // 编辑模式下的保存按钮
                    Button {
                        text: "保存更改"
                        visible: studentDetailDialog.isEditMode
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 36
                            radius: 6
                            color: successColor
                        }
                        
                        contentItem: Text {
                            text: "保存更改"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            // 表单验证
                            if (!editIdField.text) {
                                notificationText.text = "请输入学号"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                return
                            }
                            
                            if (!editNameField.text) {
                                notificationText.text = "请输入姓名"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                return
                            }
                            
                            // 创建更新数据
                            var updateData = {
                                id: editIdField.text,
                                name: editNameField.text,
                                gender: editGenderField.currentText,
                                age: editAgeField.value,
                                department: editDepartmentField.text,
                                scores: studentDetailDialog.studentData.scores || {}
                            };
                            
                            // 如果学号有变更，需要特殊处理
                            if (studentDetailDialog.originalId !== editIdField.text) {
                                // 先删除原记录
                                try {
                                    studentManager.delete_student(studentDetailDialog.originalId);
                                    
                                    // 添加新记录
                                    studentManager.add_student(updateData);
                                    
                                    // 更新模型
                                    for (var i = 0; i < studentModel.count; i++) {
                                        if (studentModel.get(i).id === studentDetailDialog.originalId) {
                                            studentModel.remove(i);
                                            studentModel.insert(i, updateData);
                                            break;
                                        }
                                    }
                                } catch (e) {
                                    console.log("更新学生失败:", e);
                                }
                            } else {
                                // 正常更新
                                try {
                                    // 创建一个不包含id的更新数据副本
                                    var updateDataForDB = {
                                        name: updateData.name,
                                        gender: updateData.gender,
                                        age: updateData.age,
                                        department: updateData.department,
                                        scores: updateData.scores
                                    };
                                    
                                    // 更新数据库
                                    studentManager.update_student(studentDetailDialog.originalId, updateDataForDB);
                                    
                                    // 更新模型 - 使用完整的updateData（包含id）
                                    for (var i = 0; i < studentModel.count; i++) {
                                        if (studentModel.get(i).id === studentDetailDialog.originalId) {
                                            for (var key in updateData) {
                                                studentModel.setProperty(i, key, updateData[key]);
                                            }
                                            break;
                                        }
                                    }
                                } catch (e) {
                                    console.log("更新学生失败:", e);
                                }
                            }
                            
                            // 显示成功通知
                            notificationText.text = "学生信息更新成功"
                            notificationColor = successColor
                            notificationAnim.start()
                            
                            // 更新对话框的数据
                            studentDetailDialog.studentData = updateData;
                            studentDetailDialog.originalId = editIdField.text;
                            
                            // 退出编辑模式
                            studentDetailDialog.isEditMode = false;
                        }
                    }
                    
                    // 取消编辑按钮
                    Button {
                        text: "取消编辑"
                        visible: studentDetailDialog.isEditMode
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: Qt.rgba(0.9, 0.9, 0.9, 1.0)
                        }
                        
                        contentItem: Text {
                            text: "取消"
                            color: textColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            // 重置表单数据为原始值并退出编辑模式
                            studentDetailDialog.fillEditForm()
                            studentDetailDialog.isEditMode = false;
                        }
                    }
                    
                    // 删除学生按钮
                    Button {
                        text: "删除"
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: dangerColor
                        }
                        
                        contentItem: Text {
                            text: "删除"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            deleteConfirmationDialog.studentId = studentDetailDialog.studentData.id
                            deleteConfirmationDialog.open()
                        }
                    }
                    
                    // 关闭按钮
                    Button {
                        text: "关闭"
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: Qt.rgba(0.9, 0.9, 0.9, 1.0)
                        }
                        
                        contentItem: Text {
                            text: "关闭"
                            color: textColor
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            studentDetailDialog.close()
                        }
                    }
                }
            }
        }
    }
    
    // 删除确认对话框
    Dialog {
        id: deleteConfirmationDialog
        title: "确认删除"
        width: 400
        height: 200
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.CloseOnEscape
        
        property string studentId: ""
        
        // 设置对话框背景
        background: Rectangle {
            radius: 8
            color: cardColor
            border.color: borderColor
            border.width: 1
        }
        
        // 确认信息
        contentItem: Item {
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                Text {
                    text: "确定要删除该学生信息吗？此操作不可恢复。"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                // 操作按钮
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    
                    Button {
                        text: "取消"
                        flat: true
                        onClicked: deleteConfirmationDialog.close()
                    }
                    
                    Button {
                        text: "删除"
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: dangerColor
                        }
                        
                        contentItem: Text {
                            text: "删除"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            // 从数据库中删除学生
                            try {
                                studentManager.delete_student(deleteConfirmationDialog.studentId)
                                
                                // 从模型中删除学生
                                for (var i = 0; i < studentModel.count; i++) {
                                    if (studentModel.get(i).id === deleteConfirmationDialog.studentId) {
                                        studentModel.remove(i)
                                        break
                                    }
                                }
                                
                                // 显示通知
                                notificationText.text = "学生删除成功"
                                notificationColor = accentColor
                                notificationAnim.start()
                                
                                // 关闭对话框
                                deleteConfirmationDialog.close()
                                studentDetailDialog.close()
                            } catch (e) {
                                console.log("删除学生失败:", e)
                                
                                // 显示错误通知
                                notificationText.text = "删除学生失败"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                
                                // 关闭对话框
                                deleteConfirmationDialog.close()
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 删除成绩确认对话框
    Dialog {
        id: deleteScoreConfirmationDialog
        title: "确认删除成绩"
        width: 400
        height: 200
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.CloseOnEscape
        
        property string studentId: ""
        property string subject: ""
        
        // 设置对话框背景
        background: Rectangle {
            radius: 8
            color: cardColor
            border.color: borderColor
            border.width: 1
        }
        
        // 确认信息
        contentItem: Item {
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                Text {
                    text: "确定要删除科目 \"" + deleteScoreConfirmationDialog.subject + "\" 的成绩吗？此操作不可恢复。"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
                
                // 操作按钮
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    
                    Button {
                        text: "取消"
                        flat: true
                        onClicked: deleteScoreConfirmationDialog.close()
                    }
                    
                    Button {
                        text: "删除"
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: dangerColor
                        }
                        
                        contentItem: Text {
                            text: "删除"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            // 删除成绩
                            try {
                                studentManager.delete_student_score(
                                    deleteScoreConfirmationDialog.studentId,
                                    deleteScoreConfirmationDialog.subject
                                )
                                
                                // 更新当前对话框中的数据
                                if (studentDetailDialog.visible && 
                                    studentDetailDialog.studentData.id === deleteScoreConfirmationDialog.studentId) {
                                    
                                    // 获取最新的学生数据
                                    var updatedStudent = studentManager.get_student(deleteScoreConfirmationDialog.studentId)
                                    if (updatedStudent) {
                                        studentDetailDialog.studentData = updatedStudent
                                        studentDetailDialog.fillEditForm()
                                    }
                                }
                                
                                // 更新列表模型中的学生数据
                                for (var i = 0; i < studentModel.count; i++) {
                                    if (studentModel.get(i).id === deleteScoreConfirmationDialog.studentId) {
                                        var currentStudent = studentModel.get(i)
                                        var updatedScores = JSON.parse(JSON.stringify(currentStudent.scores || {}))
                                        delete updatedScores[deleteScoreConfirmationDialog.subject]
                                        
                                        // 更新模型
                                        studentModel.setProperty(i, "scores", updatedScores)
                                        break
                                    }
                                }
                                
                                // 显示成功通知
                                notificationText.text = "成绩删除成功"
                                notificationColor = accentColor
                                notificationAnim.start()
                                
                                // 关闭对话框
                                deleteScoreConfirmationDialog.close()
                            } catch (e) {
                                console.log("删除成绩失败:", e)
                                
                                // 显示错误通知
                                notificationText.text = "删除成绩失败"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                
                                // 关闭对话框
                                deleteScoreConfirmationDialog.close()
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 添加成绩对话框
    Dialog {
        id: addScoreDialog
        title: studentIndex >= 0 ? "编辑成绩" : "添加成绩"
        width: 400
        height: 300
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.CloseOnEscape
        
        property string studentId: ""
        property string subjectName: ""
        property int scoreValue: 0
        property int studentIndex: -1
        
        onOpened: {
            if (studentIndex >= 0) {
                // 编辑模式，填充现有数据
                subjectField.text = subjectName
                scoreField.value = scoreValue
            } else {
                // 添加模式，清空表单
                subjectField.text = ""
                scoreField.value = 0
            }
        }
        
        // 设置对话框背景
        background: Rectangle {
            radius: 8
            color: cardColor
            border.color: borderColor
            border.width: 1
        }
        
        // 添加成绩表单
        contentItem: Item {
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                
                // 成绩表单
                GridLayout {
                    columns: 2
                    columnSpacing: 15
                    rowSpacing: 15
                    Layout.fillWidth: true
                    
                    Text { text: "科目:" }
                    TextField { 
                        id: subjectField
                        Layout.fillWidth: true 
                        placeholderText: "请输入科目名称"
                    }
                    
                    Text { text: "成绩:" }
                    SpinBox { 
                        id: scoreField
                        from: 0
                        to: 100
                        value: 0
                        Layout.fillWidth: true 
                    }
                    
                    Text { text: "等级:" }
                    Text { 
                        text: studentManager ? studentManager.calculate_grade(scoreField.value) : "N/A"
                        font.bold: true
                        color: {
                            if (scoreField.value >= 90) return "#4CAF50"
                            if (scoreField.value >= 80) return "#8BC34A"
                            if (scoreField.value >= 70) return "#FFC107"
                            if (scoreField.value >= 60) return "#FF9800"
                            return "#F44336"
                        }
                    }
                }
                
                // 操作按钮
                RowLayout {
                    Layout.alignment: Qt.AlignRight
                    spacing: 10
                    
                    Button {
                        text: "取消"
                        flat: true
                        onClicked: addScoreDialog.close()
                    }
                    
                    Button {
                        text: "保存"
                        
                        background: Rectangle {
                            implicitWidth: 80
                            implicitHeight: 36
                            radius: 6
                            color: accentColor
                        }
                        
                        contentItem: Text {
                            text: "保存"
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            // 表单验证
                            if (!subjectField.text) {
                                notificationText.text = "请输入科目名称"
                                notificationColor = dangerColor
                                notificationAnim.start()
                                return
                            }
                            
                            // 如果是编辑模式且科目名称有变化，需要先删除旧的科目
                            if (addScoreDialog.studentIndex >= 0 && 
                                addScoreDialog.subjectName !== subjectField.text) {
                                
                                try {
                                    // 删除旧科目
                                    studentManager.delete_student_score(
                                        addScoreDialog.studentId,
                                        addScoreDialog.subjectName
                                    )
                                } catch (e) {
                                    console.log("删除旧科目失败:", e)
                                }
                            }
                            
                            // 更新学生成绩
                            try {
                                studentManager.update_student_score(
                                    addScoreDialog.studentId,
                                    subjectField.text,
                                    scoreField.value
                                )
                                
                                // 更新学生详情对话框
                                if (studentDetailDialog.visible && 
                                    studentDetailDialog.studentData.id === addScoreDialog.studentId) {
                                    
                                    // 获取最新的学生数据
                                    var updatedStudent = studentManager.get_student(addScoreDialog.studentId)
                                    if (updatedStudent) {
                                        studentDetailDialog.studentData = updatedStudent
                                        studentDetailDialog.fillEditForm()
                                    }
                                }
                                
                                // 更新列表模型中的学生数据
                                for (var i = 0; i < studentModel.count; i++) {
                                    if (studentModel.get(i).id === addScoreDialog.studentId) {
                                        var currentStudent = studentModel.get(i)
                                        var updatedScores = JSON.parse(JSON.stringify(currentStudent.scores || {}))
                                        
                                        // 如果是编辑模式且科目名称有变化，需要删除旧的科目
                                        if (addScoreDialog.studentIndex >= 0 && 
                                            addScoreDialog.subjectName !== subjectField.text) {
                                            delete updatedScores[addScoreDialog.subjectName]
                                        }
                                        
                                        // 更新或添加新科目成绩
                                        updatedScores[subjectField.text] = scoreField.value
                                        
                                        // 更新模型
                                        studentModel.setProperty(i, "scores", updatedScores)
                                        break
                                    }
                                }
                                
                                // 显示成功通知
                                var actionText = addScoreDialog.studentIndex >= 0 ? "更新" : "添加"
                                notificationText.text = "成绩" + actionText + "成功"
                                notificationColor = accentColor
                                notificationAnim.start()
                                
                                // 关闭对话框
                                addScoreDialog.close()
                            } catch (e) {
                                console.log("更新成绩失败:", e)
                                
                                // 显示错误通知
                                notificationText.text = "更新成绩失败"
                                notificationColor = dangerColor
                                notificationAnim.start()
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 通知文本
    Rectangle {
        id: notificationContainer
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50
        width: notificationText.contentWidth + 30
        height: notificationText.contentHeight + 20
        radius: 8
        color: notificationColor
        opacity: 0
        z: 1000  // 确保在最顶层
        
        Text {
            id: notificationText
            text: ""
            color: "white"
            font.pixelSize: 14
            font.family: "Microsoft YaHei, SimHei, Arial"  // 指定支持中文的字体
            anchors.centerIn: parent
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        
        // 定义动画
        SequentialAnimation on opacity {
            id: notificationAnim
            running: false
            
            NumberAnimation {
                to: 1
                duration: 300
            }
            
            PauseAnimation {
                duration: 2000
            }
            
            NumberAnimation {
                to: 0
                duration: 300
            }
        }
    }
    
    // 加载数据
    Component.onCompleted: {
        // 尝试从数据库加载学生数据
        try {
            var students = studentManager.get_all_students()
            if (students && students.length) {
                // 清空当前模型
                studentModel.clear()
                
                // 添加从数据库加载的学生
                for (var i = 0; i < students.length; i++) {
                    studentModel.append(students[i])
                }
                
                // 显示通知
                notificationText.text = "已加载 " + students.length + " 名学生"
                notificationColor = accentColor
                notificationAnim.start()
            }
        } catch (e) {
            console.log("加载学生数据失败:", e)
        }
    }
    
    // 统计对话框
    Dialog {
        id: statisticsDialog
        title: "成绩统计"
        width: 1000
        height: 800
        anchors.centerIn: parent
        modal: true
        closePolicy: Popup.CloseOnEscape
        
        property var statistics: ({})
        
        onOpened: {
            statistics = studentManager.get_statistics();
        }
        
        background: Rectangle {
            radius: 8
            color: cardColor
            border.color: borderColor
            border.width: 1
        }
        
        contentItem: ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 20
            
            // 总体统计卡片
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 140
                radius: 8
                color: Qt.rgba(0.97, 0.97, 0.99, 1.0)
                border.color: borderColor
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 10
                    
                    Text {
                        text: "总体统计"
                        font.pixelSize: 18
                        font.weight: Font.Bold
                        color: textColor
                    }
                    
                    GridLayout {
                        columns: 7
                        Layout.fillWidth: true
                        columnSpacing: 10
                        rowSpacing: 10
                        
                        // 学生总数
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "学生总数"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: statisticsDialog.statistics.totalStudents || 0
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: accentColor
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                        
                        // 科目总数
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "科目总数"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: statisticsDialog.statistics.totalSubjects || 0
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: warningColor
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                        
                        // 平均分
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "平均分"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: (statisticsDialog.statistics.averageScore || 0).toFixed(1)
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: {
                                        var avg = statisticsDialog.statistics.averageScore || 0;
                                        if (avg >= 90) return "#4CAF50";
                                        if (avg >= 80) return "#8BC34A";
                                        if (avg >= 70) return "#FFC107";
                                        if (avg >= 60) return "#FF9800";
                                        return "#F44336";
                                    }
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                        
                        // 最高分
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "最高分"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: statisticsDialog.statistics.highestScore || 0
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: "#4CAF50"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                        
                        // 最低分
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "最低分"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: statisticsDialog.statistics.lowestScore || 100
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: "#F44336"
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                        
                        // 及格率
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "及格率"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: (statisticsDialog.statistics.passRate || 0).toFixed(1) + "%"
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: {
                                        var rate = statisticsDialog.statistics.passRate || 0;
                                        if (rate >= 90) return "#4CAF50";
                                        if (rate >= 80) return "#8BC34A";
                                        if (rate >= 60) return "#FFC107";
                                        if (rate >= 40) return "#FF9800";
                                        return "#F44336";
                                    }
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                        
                        // 成绩总数
                        Rectangle {
                            Layout.preferredWidth: 110
                            Layout.preferredHeight: 80
                            radius: 6
                            color: Qt.rgba(0.98, 0.98, 1.0, 0.8)
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 5
                                
                                Text {
                                    text: "成绩总数"
                                    font.pixelSize: 12
                                    color: Qt.rgba(0, 0, 0, 0.6)
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                                
                                Text {
                                    text: statisticsDialog.statistics.totalScores || 0
                                    font.pixelSize: 22
                                    font.weight: Font.Bold
                                    color: accentColor
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                    }
                }
            }
            
            // 按科目统计
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 8
                color: Qt.rgba(0.97, 0.97, 0.99, 1.0)
                border.color: borderColor
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 10
                    
                    Text {
                        text: "按科目统计"
                        font.pixelSize: 18
                        font.weight: Font.Bold
                        color: textColor
                    }
                    
                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        
                        model: {
                            var subjectStatsModel = [];
                            var subjects = statisticsDialog.statistics.subjects || {};
                            
                            for (var subject in subjects) {
                                if (subjects.hasOwnProperty(subject)) {
                                    subjectStatsModel.push({
                                        subject: subject,
                                        stats: subjects[subject]
                                    });
                                }
                            }
                            
                            subjectStatsModel.sort(function(a, b) {
                                return b.stats.average - a.stats.average;
                            });
                            
                            return subjectStatsModel;
                        }
                        
                        header: Rectangle {
                            width: parent.width
                            height: 40
                            color: Qt.rgba(0.95, 0.95, 0.97, 1.0)
                            border.width: 1
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Row {
                                anchors.fill: parent
                                
                                Text {
                                    text: "科目名称"
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 150
                                    height: parent.height
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 10
                                }
                                
                                Text {
                                    text: "人数"
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    text: "平均分"
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    text: "最高分"
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    text: "最低分"
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    text: "及格率"
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                        
                        delegate: Rectangle {
                            width: parent.width
                            height: 40
                            color: index % 2 === 0 ? Qt.rgba(0.98, 0.98, 1.0, 1.0) : Qt.rgba(1, 1, 1, 1.0)
                            border.width: 1
                            border.color: Qt.rgba(0, 0, 0, 0.1)
                            
                            Row {
                                anchors.fill: parent
                                
                                Text {
                                    text: modelData.subject
                                    font.pixelSize: 14
                                    width: 150
                                    height: parent.height
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 10
                                    elide: Text.ElideRight
                                }
                                
                                Text {
                                    text: modelData.stats.count
                                    font.pixelSize: 14
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                Text {
                                    text: modelData.stats.average.toFixed(1)
                                    font.pixelSize: 14
                                    font.weight: Font.Medium
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    color: {
                                        var avg = modelData.stats.average;
                                        if (avg >= 90) return "#4CAF50";
                                        if (avg >= 80) return "#8BC34A";
                                        if (avg >= 70) return "#FFC107";
                                        if (avg >= 60) return "#FF9800";
                                        return "#F44336";
                                    }
                                }
                                
                                Text {
                                    text: modelData.stats.highest
                                    font.pixelSize: 14
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    color: "#4CAF50"
                                }
                                
                                Text {
                                    text: modelData.stats.lowest
                                    font.pixelSize: 14
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    color: modelData.stats.lowest < 60 ? "#F44336" : "#8BC34A"
                                }
                                
                                Text {
                                    text: modelData.stats.passRate.toFixed(1) + "%"
                                    font.pixelSize: 14
                                    width: 100
                                    height: parent.height
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    color: {
                                        var rate = modelData.stats.passRate;
                                        if (rate >= 90) return "#4CAF50";
                                        if (rate >= 80) return "#8BC34A";
                                        if (rate >= 60) return "#FFC107";
                                        if (rate >= 40) return "#FF9800";
                                        return "#F44336";
                                    }
                                }
                            }
                        }
                        
                        // 空列表提示
                        Rectangle {
                            width: parent.width
                            height: 60
                            color: "transparent"
                            visible: parent.count === 0
                            
                            Text {
                                text: "暂无科目数据"
                                color: Qt.rgba(0, 0, 0, 0.5)
                                font.pixelSize: 16
                                anchors.centerIn: parent
                            }
                        }
                    }
                }
            }
            
            // 关闭按钮
            RowLayout {
                Layout.alignment: Qt.AlignRight
                
                Button {
                    text: "关闭"
                    
                    background: Rectangle {
                        implicitWidth: 80
                        implicitHeight: 36
                        radius: 6
                        color: Qt.rgba(0.9, 0.9, 0.9, 1.0)
                    }
                    
                    contentItem: Text {
                        text: "关闭"
                        color: textColor
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        statisticsDialog.close()
                    }
                }
            }
        }
    }
}
