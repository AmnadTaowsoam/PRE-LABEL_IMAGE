# CORNINSPEC-LABEL-IMAGE

## docker-compose
- run docker-compose.yml
  
      docker-compose up -d

## กรณีที่พบปัญหา token หมดอายุ หรือ label-studio ไม่ทำงาน
1. ให้ทำการเริ่มทำงาน

        docker-compose up -d

2. ให้เข้าไปที่ http://localhost:8080/user/account ทำการ copy Access Token มาเก็บไว้ที่ .env
3. หยุดการทำงาน 

        docker-compose down

4. ให้ทำการเริ่มทำงานอีกครั้ง

        docker-compose up -d

    token จะถูกเก็บไปในไว้ใน volume

## ตั้งค่า Model ใน Label Studio
1. เข้าสู่ระบบ Label Studio:
    - เปิด Label Studio ในเบราว์เซอร์ของคุณ
2. ไปที่เมนู Model:
    - เลือกโปรเจคที่คุณต้องการเชื่อมต่อกับ ML backend
    - คลิกที่ไอคอน Settings หรือไปที่เมนู Model ในแถบด้านซ้าย

3. ตั้งค่า ML backend:
    - คลิกที่ปุ่ม Add Model
    - กรอกข้อมูลการเชื่อมต่อ ML backend ของคุณ:
        - URL: ใส่ URL ของ ML backend ของคุณ เช่น http://pre-label-model:7000
        - Title: ใส่ชื่อที่คุณต้องการสำหรับ ML backend นี้
        - Description: ใส่คำอธิบาย (ถ้าต้องการ)
    - คลิก Save เพื่อบันทึกการตั้งค่า
4. ทดสอบการเชื่อมต่อ:
    - หลังจากบันทึกการตั้งค่าแล้ว Label Studio จะทำการทดสอบการเชื่อมต่อกับ ML backend โดยอัตโนมัติ
    - หากการเชื่อมต่อสำเร็จ คุณจะเห็นสถานะว่า Active

## ตั้งค่า Annotation ใน Label Studio
1. ไปที่เมนู Annotation:
    - จากหน้าการตั้งค่าโปรเจค ให้คลิกที่ Annotation ในแถบด้านซ้าย
2. ตั้งค่าเพื่อใช้งานโมเดลสำหรับการ prelabeling:
    - ในหน้า Annotation ให้หาส่วนที่เกี่ยวข้องกับการตั้งค่าการใช้โมเดลในการทำนายล่วงหน้า (prelabeling)
    - ตั้งค่าการใช้โมเดลในการทำนายผลลัพธ์ล่วงหน้า (prelabeling) ตามที่ Label Studio ให้คุณตั้งค่า
3. บันทึกการตั้งค่า:
    - หลังจากทำการตั้งค่าเสร็จสิ้น ให้คลิก Save เพื่อบันทึกการตั้งค่า
4. ทดสอบการทำนายผลล่วงหน้า:
    - กลับไปที่ Data Manager และเลือกงาน (tasks) ที่คุณต้องการทำนาย
    - คลิกที่เมนู Actions แล้วเลือก Retrieve predictions เพื่อดึงผลลัพธ์การทำนายจากโมเดล


## ตั้งค่า Webhook ใน Label Studio
- ไปที่ Settings ของโปรเจคใน Label Studio.
- เลือก Webhooks.
- เพิ่ม Webhook URL: http://webhook-service:7001/webhook

## ตั้งค่า Label

<View>
    <View style="display:flex;align-items:start;gap:8px;flex-direction:row">
        <Image name="image" value="$image" zoom="true" zoomControl="true" rotateControl="true"/>
        <View>
            <Filter toName="label" minlength="0" name="filter"/>
            <RectangleLabels name="label" toName="image" showInline="false">
                <Label value="0" background="#c6d30d"/>
                <Label value="1" background="#D4380D"/>
                <Label value="2" background="#0d2ed3"/>
                <Label value="3" background="#14a769"/>
                <Label value="4" background="#ff6347"/>
                <Label value="5" background="#ffa500"/>
                <Label value="6" background="#8a2be2"/>
                <Label value="7" background="#ff69b4"/>
                <Label value="36" background="#2e8b57"/>
                <Label value="37" background="#4682b4"/>
                <Label value="38" background="#d2691e"/>
                <Label value="39" background="#5f9ea0"/>
                <Label value="40" background="#ff4500"/>
            </RectangleLabels>
        </View>
    </View>
</View>