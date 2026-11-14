"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { Department } from "@/shared/types/department";
import { prefixBaseApiPath } from "@/shared/utils/path";
import { useAuth } from "@/context/GlobalContext";

interface DepartmentContextType {
    departments: Department[];
    currentDepartment: Department | null;
    setDepartment: (mnemonic: string) => void;
}

const DepartmentContext = createContext<DepartmentContextType | undefined>(undefined);

export const DepartmentContextProvider = ({ children }: { children: ReactNode }) => {
    const { profile } = useAuth();
    const [departments, setDepartments] = useState<Department[]>([]);
    const [currentDepartment, setCurrentDepartment] = useState<Department | null>(null);

    const loadDepartments = async () => {
        const storedDepartments = localStorage.getItem("departments");
        const storedCurrentDept = localStorage.getItem("currentDepartment");

        if (storedDepartments) {
            const deptList: Department[] = JSON.parse(storedDepartments);
            setDepartments(deptList);

            if (storedCurrentDept) {
                setCurrentDepartment(JSON.parse(storedCurrentDept));
            } else {
                setCurrentDepartment(deptList[0]);
                localStorage.setItem("currentDepartment", JSON.stringify(deptList[0]));
            }
            return;
        }

        const res = await fetch(prefixBaseApiPath("/departments"), { method: "POST" });

        if (!res.ok) return;

        const list: Department[] = await res.json();

        setDepartments(list);
        localStorage.setItem("departments", JSON.stringify(list));

        const initialDept = storedCurrentDept ? JSON.parse(storedCurrentDept) : list[0];
        setCurrentDepartment(initialDept);
        localStorage.setItem("currentDepartment", JSON.stringify(initialDept));
    };

    useEffect(() => {
        if (!profile) {
            localStorage.removeItem("departments");
            localStorage.removeItem("currentDepartment");
            return;
        }
        loadDepartments();
    }, [profile]);

    const setDepartment = (mnemonic: string) => {
        const dept = departments.find((d) => d.department_mnemonic === mnemonic);
        if (!dept) return;
        setCurrentDepartment(dept);
        localStorage.setItem("currentDepartment", JSON.stringify(dept));
    };

    return (
        <DepartmentContext.Provider
            value={{
                departments,
                currentDepartment,
                setDepartment,
            }}
        >
            {children}
        </DepartmentContext.Provider>
    );
};

export const useDepartmentContext = () => {
    const ctx = useContext(DepartmentContext);
    if (!ctx) throw new Error("useDepartmentContext must be used inside DepartmentContextProvider");
    return ctx;
};

export const useDepartment = () => {
    const { departments, currentDepartment, setDepartment } = useDepartmentContext();
    return { departments, currentDepartment, setDepartment };
};
