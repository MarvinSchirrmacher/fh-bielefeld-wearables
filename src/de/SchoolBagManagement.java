package de;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Map;

public class SchoolBagManagement extends JFrame implements ActionListener {

    private String htmlBefore = "<html><body style=\"padding:20px;height:20px;\">";
    private String htmlAfter = "</body></html>";

    public SchoolBagManagement(String title) {
        super(title);

        initializeFrame();
        initializePane();
    }

    private void initializePane() {
        JLabel firstTabLabel = new JLabel("Pack your school bag");
        JLabel secondTabLabel = new JLabel("Trim your school bag");
        JLabel thirdTabLabel = new JLabel("Manage your data");

        JPanel firstTab = new JPanel() {{
            add(firstTabLabel);
        }};
        JPanel secondTab = new JPanel() {{
            add(secondTabLabel);
        }};
        JPanel thirdTab = new JPanel() {{
            add(thirdTabLabel);
        }};

        JTabbedPane pane = new JTabbedPane() {{
            addTab(htmlBefore + "Pack" + htmlAfter, firstTab);
            addTab(htmlBefore + "Trim" + htmlAfter, secondTab);
            addTab(htmlBefore + "Manage" + htmlAfter, thirdTab);
        }};
        getContentPane().add(pane);
    }

    private void initializeFrame() {
        this.setExtendedState(JFrame.MAXIMIZED_BOTH);
        this.setUndecorated(true);
        this.setVisible(true);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }

    @Override
    public void actionPerformed(ActionEvent e) {

    }
}
