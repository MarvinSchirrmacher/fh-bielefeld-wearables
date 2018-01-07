package de;

import com.google.gson.Gson;
import com.google.gson.stream.JsonReader;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.FileNotFoundException;
import java.io.FileReader;

public class SchoolBagManagement extends JFrame implements ActionListener {
    SchoolBagSettings settings;

    SchoolBagManagement(String title, String settingsFilePath) throws FileNotFoundException {
        super(title);

        loadSettings(settingsFilePath);
        initializeFrame();
        initializePane();
    }

    private void loadSettings(String filePath) throws FileNotFoundException {
        Gson gson = new Gson();
        JsonReader reader = new JsonReader(new FileReader(filePath));
        this.settings = gson.fromJson(reader, SchoolBagSettings.class);
    }

    private void initializePane() {
        JTabbedPane pane = new JTabbedPane();
        pane.addTab(format("Pack"), new PackingTab(this));
        pane.addTab(format("Trim"), new TrimmingTab(this));
        pane.addTab(format("Manage"), new ConfigurationTab(this, this.settings));
        getContentPane().add(pane);
    }

    private void initializeFrame() {
        this.setExtendedState(JFrame.MAXIMIZED_BOTH);
        this.setUndecorated(true);
        this.setVisible(true);
        this.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
    }

    @Override
    public void actionPerformed(ActionEvent e) {

    }

    private static String format(String label) {
        String htmlBefore = "<html><body style=\"padding:20px;height:20px;\">";
        String htmlAfter = "</body></html>";
        return htmlBefore + label + htmlAfter;
    }
}
