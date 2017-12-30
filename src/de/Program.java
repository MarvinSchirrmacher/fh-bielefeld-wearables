package de;

import javax.swing.SwingUtilities;

/**
 * Grafische Benutzerschnittstelle zur Bedienung und Konfiguration der intelligenten Schultasche.
 *
 * @author MarvinSchirrmacher
 * @since 30-12-2017
 *
 */
public class Program {
    /**
     * Programmeinstiegspunkt, der die eigentliche GUI-Anwendung startet.
     *
     * @param args Die optionalen Kommandozeilenparamter.
     */
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SchoolBagManagement("Intelligente Schultasche"));
    }
}
