import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;

public class Prescription {

    private int prescID;
    private String firstName;
    private String lastName;
    private String address;
    private float sphere;
    private float axis;
    private float cylinder;
    private Date examinationDate;
    private String optometrist;
    private ArrayList<String> postRemarks; // Declare the postRemarks list

    // Constructor
    public Prescription() {
        this.postRemarks = new ArrayList<>(); // Initialize postRemarks
    }

    // Setters for the fields
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public void setSphere(float sphere) {
        this.sphere = sphere;
    }

    public void setAxis(float axis) {
        this.axis = axis;
    }

    public void setCylinder(float cylinder) {
        this.cylinder = cylinder;
    }

    public void setExaminationDate(Date examinationDate) {
        this.examinationDate = examinationDate;
    }

    public void setOptometrist(String optometrist) {
        this.optometrist = optometrist;
    }

    // Method to add a prescription
    public boolean addPrescription() {
        // Validate first and last name
        if (firstName == null || firstName.length() < 4 || firstName.length() > 15) {
            return false;
        }
        if (lastName == null || lastName.length() < 4 || lastName.length() > 15) {
            return false;
        }

        // Validate address
        if (address == null || address.length() < 20) {
            return false;
        }

        // Validate sphere, cylinder, and axis
        if (sphere < -20.00 || sphere > 20.00) {
            return false;
        }
        if (cylinder < -4.00 || cylinder > 4.00) {
            return false;
        }
        if (axis < 0 || axis > 180) {
            return false;
        }

        // Validate optometrist name
        if (optometrist == null || optometrist.length() < 8 || optometrist.length() > 25) {
            return false;
        }

        // If all conditions are met, write the prescription to the file
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("presc.txt", true))) {
            writer.write(firstName + " " + lastName + ", " + address + ", Sphere: " + sphere + 
                         ", Cylinder: " + cylinder + ", Axis: " + axis + ", Date: " + examinationDate + 
                         ", Optometrist: " + optometrist + "\n");
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }

        return true;
    }

    // Method to add a remark
    public boolean addRemark(String remark, String category) {
        // Show the full remark to ensure it is processed correctly
        System.out.println("Remark: '" + remark + "'");
        
        // Validate the remark: Must be 6 to 20 words, and first letter of the first word must be uppercase
        String[] words = remark.trim().split("\\s+");
        
        // Show the word count for debugging
        System.out.println("Word count: " + words.length);
        
        // Show each word to ensure proper splitting
        for (int i = 0; i < words.length; i++) {
            System.out.println("Word " + (i + 1) + ": " + words[i]);
        }
        
        if (words.length < 6 || words.length > 20) {
            System.out.println("Remark validation failed: Word count is out of range.");
            return false;
        }
        
        if (!Character.isUpperCase(remark.trim().charAt(0))) {
            System.out.println("Remark validation failed: First letter is not uppercase.");
            return false;
        }

        // Validate the category: Must be either "Client" or "Optometrist"
        if (!category.equals("Client") && !category.equals("Optometrist")) {
            System.out.println("Category validation failed: Invalid category.");
            return false;
        }

        // Check if more than 2 remarks have already been added
        if (postRemarks.size() >= 2) {
            System.out.println("Cannot add more remarks. Current count: " + postRemarks.size());
            return false;
        }

        // If all conditions are met, add the remark and write it to a file
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("remark.txt", true))) {
            writer.write(category + ": " + remark + "\n");
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }

        // Add the remark to the ArrayList
        postRemarks.add(remark);
        System.out.println("Remark added. Current remark count after adding: " + postRemarks.size());
        return true;
    }
}
