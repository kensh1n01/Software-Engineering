import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Date;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.File;
public class PrescriptionTest {

    private Prescription prescription;
    
    @BeforeEach
    public void setup() {
        prescription = new Prescription();
    }
    
    // Method to write test results to a file
    public void writeTestResult(String testName, String testData, String expectedResult, String actualResult, boolean isPass) {
        File file = new File("TestResultTable.txt");
        boolean isNewFile = !file.exists();  // Check if the file already exists

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file, true))) {
            // If it's a new file, write the header first
            if (isNewFile) {
                writer.write(String.format("%-40s%-80s%-60s%-40s%-10s\n", 
                    "Test Cases", "Test Data", "Expected Result", "Test Result", "Pass/Fail"));
                writer.write("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n");
            }

            // Write the test result data
            writer.write(String.format("%-40s%-80s%-60s%-40s%-10s\n", 
                testName, testData, expectedResult, actualResult, (isPass ? "Pass" : "Fail")));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Your test cases remain the same...
    @Test
    public void testAddPrescription_Successful() {
        prescription.setFirstName("Himura");
        prescription.setLastName("Kenshin");
        prescription.setAddress("555 Swanston Street, Melbourne, VIC 3000, Australia");
        prescription.setSphere(-5.0f);
        prescription.setCylinder(2.0f);
        prescription.setAxis(90);
        prescription.setExaminationDate(new Date());
        prescription.setOptometrist("Dr. Lisa Lucky");

        boolean result = prescription.addPrescription();
        assertTrue(result);

        String testData = "First Name: Himura, Last Name: Kenshin, Address: 555 Swanston Street";
        String expectedResult = "Prescription added successfully";
        String actualResult = result ? "Prescription added" : "Prescription not added";
        writeTestResult("testAddPrescription_Successful", testData, expectedResult, actualResult, result);
    }

    @Test
    public void testAddPrescription_FirstNameTooShort() {
        prescription.setFirstName("Hi");
        prescription.setLastName("Kenshin");
        prescription.setAddress("555 Swanston Street, Melbourne, VIC 3000, Australia");
        prescription.setSphere(-5.0f);
        prescription.setCylinder(2.0f);
        prescription.setAxis(90);
        prescription.setExaminationDate(new Date());
        prescription.setOptometrist("Dr. Lisa Lucky");

        boolean result = prescription.addPrescription();
        assertFalse(result);

        String testData = "First Name: Hi, Last Name: Ken, Address: 555 Swanston Street";
        String expectedResult = "Prescription not added (First name too short)";
        String actualResult = result ? "Prescription added" : "Prescription not added";
        writeTestResult("testAddPrescription_FirstNameTooShort", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddPrescription_AddressTooShort() {
        prescription.setFirstName("Himura");
        prescription.setLastName("Kenshin");
        prescription.setAddress("555 Street");
        prescription.setSphere(-5.0f);
        prescription.setCylinder(2.0f);
        prescription.setAxis(90);
        prescription.setExaminationDate(new Date());
        prescription.setOptometrist("Dr. Lisa Lucky");

        boolean result = prescription.addPrescription();
        assertFalse(result);

        String testData = "First Name: Himura, Last Name: Kenshin, Address: 555 Street, Sphere: -5..";
        String expectedResult = "Prescription not added (Address too short)";
        String actualResult = result ? "Prescription added" : "Prescription not added";
        writeTestResult("testAddPrescription_FirstNameTooShort", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddPrescription_InvalidSphereValue() {
        prescription.setFirstName("Himura");
        prescription.setLastName("Kenshin");
        prescription.setAddress("555 Swanston Street, Melbourne, VIC 3000, Australia, Sphere: -5..");
        prescription.setSphere(25.0f);
        prescription.setCylinder(2.0f);
        prescription.setAxis(90);
        prescription.setExaminationDate(new Date());
        prescription.setOptometrist("Dr. Lisa Lucky");

        boolean result = prescription.addPrescription();
        assertFalse(result);

        String testData = "First Name: Himura, Last Name: Kenshin, Address: 555 Street, Sphere: 25..";
        String expectedResult = "Prescription not added (Sphere out of range)";
        String actualResult = result ? "Prescription added" : "Prescription not added";
        writeTestResult("testAddPrescription_FirstNameTooShort", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddPrescription_InvalidOptometristName() {
        prescription.setFirstName("Himura");
        prescription.setLastName("Kenshin");
        prescription.setAddress("555 Swanston Street, Melbourne, VIC 3000, Australia");
        prescription.setSphere(-5.0f);
        prescription.setCylinder(2.0f);
        prescription.setAxis(90);
        prescription.setExaminationDate(new Date());
        prescription.setOptometrist("Dr. L");

        boolean result = prescription.addPrescription();
        assertFalse(result);

        String testData = "First Name: Himura, Last Name: Kenshin, Address: 555 Street, Sphere: -5..";
        String expectedResult = "Prescription not added (Too short optometrist name)";
        String actualResult = result ? "Prescription added" : "Prescription not added";
        writeTestResult("testAddPrescription_FirstNameTooShort", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddPrescription_InvalidAxisValue() {
        prescription.setFirstName("Himura");
        prescription.setLastName("Kenshin");
        prescription.setAddress("555 Swanston Street, Melbourne, VIC 3000, Australia");
        prescription.setSphere(-5.0f);
        prescription.setCylinder(2.0f);
        prescription.setAxis(190);
        prescription.setExaminationDate(new Date());
        prescription.setOptometrist("Dr. Lisa Lucky");

        boolean result = prescription.addPrescription();
        assertFalse(result);

        String testData = "First Name: Himura, Last Name: Kenshin, Address: 555 Street, Sphere: -5..";
        String expectedResult = "Prescription not added (Axis out of range)";
        String actualResult = result ? "Prescription added" : "Prescription not added";
        writeTestResult("testAddPrescription_FirstNameTooShort", testData, expectedResult, actualResult, !result);
    }

    // Tests for addRemark
    @Test
    public void testAddRemark_Successful() {
        String remark = "This is a valid remark from the client.";
        String category = "Client";
        boolean result = prescription.addRemark(remark, category);
        assertTrue(result);

        String testData = "Remark: " + remark + ", Category: " + category;
        String expectedResult = "Remark added successfully";
        String actualResult = result ? "Remark added" : "Remark not added";
        writeTestResult("testAddRemark_Successful", testData, expectedResult, actualResult, result);
    }

    @Test
    public void testAddRemark_RemarkTooShort() {
        String remark = "Short remark.";
        String category = "Client";
        boolean result = prescription.addRemark(remark, category);
        assertFalse(result);

        String testData = "Remark: " + remark + ", Category: " + category;
        String expectedResult = "Remark not added (Remark too short)";
        String actualResult = result ? "Remark added" : "Remark not added";
        writeTestResult("testAddRemark_RemarkTooShort", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddRemark_InvalidCategory() {
        String remark = "This is a valid remark from the client.";
        String category = "Doctor";
        boolean result = prescription.addRemark(remark, category);
        assertFalse(result);

        String testData = "Remark: " + remark + ", Category: " + category;
        String expectedResult = "Remark not added (Invalid category)";
        String actualResult = result ? "Remark added" : "Remark not added";
        writeTestResult("testAddRemark_InvalidCategory", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddRemark_RemarkNotCapitalized() {
        String remark = "this is a valid remark but not capitalized.";
        String category = "Client";
        boolean result = prescription.addRemark(remark, category);
        assertFalse(result);

        String testData = "Remark: " + remark + ", Category: " + category;
        String expectedResult = "Remark not added (First word not capitalized)";
        String actualResult = result ? "Remark added" : "Remark not added";
        writeTestResult("testAddRemark_RemarkNotCapitalized", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddRemark_TooManyRemarks() {
        prescription.addRemark("This is the first valid remark.", "Client");
        prescription.addRemark("This is the second valid remark.", "Optometrist");

        // Trying to add a third remark (which should fail)
        String newRemark = "This is the third remark which should fail.";
        String category = "Client";
        boolean result = prescription.addRemark(newRemark, category);
        assertFalse(result);

        String testData = "Remark: " + newRemark + ", Category: " + category;
        String expectedResult = "Remark not added (Too many remarks)";
        String actualResult = result ? "Remark added" : "Remark not added";
        writeTestResult("testAddRemark_TooManyRemarks", testData, expectedResult, actualResult, !result);
    }

    @Test
    public void testAddRemark_RemarkTooLong() {
        String remark = "This is a very long remark k k k k k k k k k k k k k k k k k k k k k k k k.";
        String category = "Client";
        boolean result = prescription.addRemark(remark, category);
        assertFalse(result);

        String testData = "Remark: " + remark + ", Category: " + category;
        String expectedResult = "Remark not added (Remark too long)";
        String actualResult = result ? "Remark added" : "Remark not added";
        writeTestResult("testAddRemark_RemarkTooLong", testData, expectedResult, actualResult, !result);
    }
}