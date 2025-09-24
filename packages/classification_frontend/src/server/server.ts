"use server";

import { Application, type ApplicationsResponse } from "@/lib/apiTypes";

const API_BASE_URL = process.env.API_BASE_URL;

export async function fetchApplications(
  page = 1,
  pageSize = 10
): Promise<ApplicationsResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

  try {
    const response = await fetch(
      `${API_BASE_URL}/org/2f0ceb85-f099-4223-b6c8-cd5465dfd185/usecase/1a5eb87f-a8b1-47f9-8ff7-59749114c045/classification?page=${page}&page_size=${pageSize}`,
      {
        method: "GET",
        headers: {
          "accept": "application/json",
        },
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      if (response.status === 504) {
        throw new Error("Request timeout - the server took too long to respond. Please try again.");
      }
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error("Request timeout - please check your connection and try again.");
      }
      console.error("Error fetching applications:", error);
      throw error;
    }

    console.error("Error fetching applications:", error);
    throw new Error("Failed to fetch applications. Please try again.");
  }
}

export async function updateUnderwriterStatus(
  applicationId: string,
  status: string,
  review: string
) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

  try {
    const response = await fetch(
      `${API_BASE_URL}/org/2f0ceb85-f099-4223-b6c8-cd5465dfd185/usecase/1a5eb87f-a8b1-47f9-8ff7-59749114c045/classification/${applicationId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "accept": "application/json",
        },
        body: JSON.stringify({
          underwriter_status: status,
          underwriter_review: review,
        }),
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      if (response.status === 504) {
        throw new Error("Request timeout - the server took too long to respond. Please try again.");
      }
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error("Request timeout - please check your connection and try again.");
      }
      console.error("Error updating underwriter status:", error);
      throw error;
    }

    console.error("Error updating underwriter status:", error);
    throw new Error("Failed to update underwriter status. Please try again.");
  }
}


export async function createApplication(
  organizationId: string,
  usecaseId: string,
  data: {
    application_type: string;
    application_id: string;
    reason_code: string;
  },
  files: (File | Blob)[]
) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for file uploads

  try {
    const formData = new FormData();
    formData.append("data", JSON.stringify(data));

    files.forEach((file, index) => {
      const maybeFile = file as unknown as { name?: string };
      const filename = maybeFile?.name || `file_${index + 1}`;
      formData.append("files", file, filename);
    });

    const response = await fetch(
      `${API_BASE_URL}/org/${organizationId}/usecase/${usecaseId}/classification`,
      {
        method: "POST",
        headers: {
          "accept": "application/json",
        },
        body: formData,
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      if (response.status === 504) {
        throw new Error("Request timeout - the server took too long to process your files. Please try again.");
      }
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error("Request timeout - please check your connection and try again.");
      }
      console.error("Error creating application:", error);
      throw error;
    }

    console.error("Error creating application:", error);
    throw new Error("Failed to create application. Please try again.");
  }
}