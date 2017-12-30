package de;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class SchoolBagManagement extends JFrame implements ActionListener {

    SchoolBagManagement(String title) {
        super(title);

        initializeFrame();
        initializePane();
    }

    private void initializePane() {
        JTabbedPane pane = new JTabbedPane();
        pane.addTab(format("Pack"), new PackingTab(this));
        pane.addTab(format("Trim"), new TrimmingTab(this));
        pane.addTab(format("Manage"), new ConfigurationTab(this));
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
